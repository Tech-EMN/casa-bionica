// ============================================================
// CASA BIÔNICA — ESP32-C3 Sensor Module (Walking Skeleton)
// ============================================================
// Hardware: ESP32-C3 + 2x VL53L0X (ToF sensors)
// Protocol: HTTP POST direct to FastAPI backend
// I2C pins: SDA=21, SCL=22
// XSHUT: GPIO4 (sensor A), GPIO5 (sensor B)
//
// Para cada ESP32-C3, mudar:
//   - SENSOR_ID (ex: "sensor-quarto-01", "sensor-banheiro-01")
//   - WIFI_SSID, WIFI_PASS
//   - API_URL (do Railway deploy)
// ============================================================

#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <VL53L0X.h>

// ── CONFIGURAÇÃO (MUDAR por sensor) ──────────────────────
const char* WIFI_SSID = "SEU_WIFI";
const char* WIFI_PASS = "SUA_SENHA";
const char* API_URL  = "https://SEU-APP.up.railway.app/ingest";
const char* SENSOR_ID = "sensor-quarto-01";  // ⚠️ MUDAR
const char* HOME_ID   = "home-001";

// ── HARDWARE ──────────────────────────────────────────────
#define SDA_PIN   21
#define SCL_PIN   22
#define XSHUT_A   4    // Sensor A (primeiro a cruzar = entrada)
#define XSHUT_B   5    // Sensor B (segundo a cruzar = saída)

VL53L0X sensorA;
VL53L0X sensorB;

// ── CONSTANTES ────────────────────────────────────────────
const int BACKGROUND_DISTANCE = 2000;  // mm — distância até parede oposta
const int CROSSING_THRESHOLD  = 800;   // mm — abaixo disso = pessoa passando
const int CROSSING_TIMEOUT_MS = 2000;  // ms — tempo máximo entre A e B (senão descarta)
const int LOOP_DELAY_MS       = 50;    // ms entre leituras

// ── STATE MACHINE ─────────────────────────────────────────
enum State {
  IDLE,
  ZONE_A_TRIGGERED,  // sensor A detectou primeiro → pessoa entrando
  ZONE_B_TRIGGERED   // sensor B detectou primeiro → pessoa saindo
};

State state = IDLE;
unsigned long triggerTime = 0;
int eventCount = 0;

// ── SETUP ─────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=== CASA BIÔNICA — ESP32-C3 ===");
  Serial.printf("Sensor ID: %s\n", SENSOR_ID);

  // Init I2C
  Wire.begin(SDA_PIN, SCL_PIN);

  // Init VL53L0X sensors com endereços diferentes
  pinMode(XSHUT_A, OUTPUT);
  pinMode(XSHUT_B, OUTPUT);

  // Reset ambos
  digitalWrite(XSHUT_A, LOW);
  digitalWrite(XSHUT_B, LOW);
  delay(10);

  // Sensor A → endereço 0x30
  digitalWrite(XSHUT_A, HIGH);
  delay(10);
  sensorA.init(true);
  sensorA.setTimeout(500);
  sensorA.setAddress(0x30);

  // Sensor B → endereço 0x31
  digitalWrite(XSHUT_B, HIGH);
  delay(10);
  sensorB.init(true);
  sensorB.setTimeout(500);
  sensorB.setAddress(0x31);

  Serial.println("VL53L0X: OK (0x30 + 0x31)");

  // Continuous mode (mais rápido que single-shot)
  sensorA.startContinuous();
  sensorB.startContinuous();

  // WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("WiFi conectando");
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 40) {
    delay(500);
    Serial.print(".");
    retries++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\nWiFi: OK (%s)\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\nWiFi: FALHOU — continuando sem rede");
  }

  Serial.println("Pronto. Monitorando passagem...\n");
}

// ── MAIN LOOP ─────────────────────────────────────────────
void loop() {
  // Lê distâncias
  int dA = sensorA.readRangeContinuousMillimeters();
  int dB = sensorB.readRangeContinuousMillimeters();

  // Timeout de leitura
  if (sensorA.timeoutOccurred() || sensorB.timeoutOccurred()) {
    delay(LOOP_DELAY_MS);
    return;
  }

  // Ignora leituras inválidas (fora de range)
  if (dA > BACKGROUND_DISTANCE || dB > BACKGROUND_DISTANCE) {
    // Se alguém estava atravessando e a distância voltou ao normal,
    // a travessia terminou
    if (state != IDLE) {
      unsigned long elapsed = millis() - triggerTime;
      if (elapsed > CROSSING_TIMEOUT_MS) {
        // Timeout — pessoa parou ou desistiu
        Serial.printf("[TIMEOUT] Travessia descartada (%lums)\n", elapsed);
        state = IDLE;
      }
    }
    delay(LOOP_DELAY_MS);
    return;
  }

  // Detecta presença nas zonas
  bool zoneA = (dA < CROSSING_THRESHOLD);
  bool zoneB = (dB < CROSSING_THRESHOLD);

  // ── State machine ───────────────────
  switch (state) {
    case IDLE:
      if (zoneA && !zoneB) {
        state = ZONE_A_TRIGGERED;
        triggerTime = millis();
      } else if (zoneB && !zoneA) {
        state = ZONE_B_TRIGGERED;
        triggerTime = millis();
      }
      break;

    case ZONE_A_TRIGGERED:
      if (zoneB) {
        // A → B = ENTRADA (pessoa entrou no ambiente)
        unsigned long elapsed = millis() - triggerTime;
        if (elapsed <= CROSSING_TIMEOUT_MS) {
          sendEvent("entry", (dA + dB) / 2, elapsed);
        }
        state = IDLE;
      } else if (millis() - triggerTime > CROSSING_TIMEOUT_MS) {
        Serial.println("[TIMEOUT] Zona A sem cruzar B");
        state = IDLE;
      }
      break;

    case ZONE_B_TRIGGERED:
      if (zoneA) {
        // B → A = SAÍDA (pessoa saiu do ambiente)
        unsigned long elapsed = millis() - triggerTime;
        if (elapsed <= CROSSING_TIMEOUT_MS) {
          sendEvent("exit", (dA + dB) / 2, elapsed);
        }
        state = IDLE;
      } else if (millis() - triggerTime > CROSSING_TIMEOUT_MS) {
        Serial.println("[TIMEOUT] Zona B sem cruzar A");
        state = IDLE;
      }
      break;
  }

  delay(LOOP_DELAY_MS);
}

// ── ENVIO HTTP POST ───────────────────────────────────────
void sendEvent(const char* direction, int distance_mm, unsigned long elapsed_ms) {
  eventCount++;
  Serial.printf("\n=== EVENTO #%d ===\n", eventCount);
  Serial.printf("  Direção:  %s\n", direction);
  Serial.printf("  Distância: %d mm\n", distance_mm);
  Serial.printf("  Tempo:    %lu ms\n", elapsed_ms);

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("  [ERRO] WiFi offline — evento perdido");
    return;
  }

  // Monta JSON manualmente (evita dependência de ArduinoJson >6)
  char json[256];
  snprintf(json, sizeof(json),
    "{\"sensor_id\":\"%s\",\"home_id\":\"%s\",\"direction\":\"%s\",\"distance_mm\":%d,\"event_timestamp\":\"%lu\"}",
    SENSOR_ID, HOME_ID, direction, distance_mm, millis()
  );
  // Nota: o campo event_timestamp com millis() é placeholder.
  // O backend converte para UTC. Para timestamp real, use NTP:
  // configTime(0, 0, "pool.ntp.org"); time_t now; time(&now);

  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(10000);

  int httpCode = http.POST(json);
  String response = http.getString();
  http.end();

  Serial.printf("  HTTP:     %d\n", httpCode);
  if (httpCode == 201) {
    Serial.println("  ✅ Evento registrado no backend");
  } else if (httpCode == 409) {
    Serial.println("  ⚠️ Evento duplicado (já existe)");
  } else {
    Serial.printf("  ❌ Erro: %d — %s\n", httpCode, response.c_str());
  }
}
