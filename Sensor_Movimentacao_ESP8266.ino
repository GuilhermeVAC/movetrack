#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// Configurações Wi-Fi e URL do servidor
const char* ssid = "Guilherme";
const char* password = "1a2b3c4d";
const char* url = "http://seu_servidor/api/sensor";

const int pirPin = D4;  // Pino do sensor PIR

WiFiClient client;
HTTPClient http;

bool lastSensorState = LOW;  // Armazena o último estado do sensor

void setup() {
  Serial.begin(115200);
  pinMode(pirPin, INPUT);

  // Conecta ao Wi-Fi com limite de tentativas
  WiFi.begin(ssid, password);
  Serial.print("Conectando ao WiFi");
  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 20) {
    delay(500);
    Serial.print(".");
    tentativas++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi conectado!");
    Serial.print("Endereço IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFalha ao conectar ao WiFi!");
  }
}

void enviarDados(int estado) {
  if (WiFi.status() == WL_CONNECTED) {
    http.begin(client, url);  // Inicia a requisição HTTP
    http.addHeader("Content-Type", "application/json");

    String jsonData = "{\"posicao_movimentada\":\"A1\", \"estado_sensor\":" + String(estado) + "}";
    int httpResponseCode = http.POST(jsonData);  // Envia os dados para o servidor

    if (httpResponseCode > 0) {
      Serial.println("Dados enviados com sucesso!");
    } else {
      Serial.print("Erro ao enviar dados. Código: ");
      Serial.println(httpResponseCode);
    }
    http.end();  // Finaliza a requisição HTTP
  } else {
    Serial.println("WiFi desconectado. Tentando reconectar...");
    WiFi.reconnect();  // Tenta reconectar de forma mais simples
  }
}

void loop() {
  // Leitura contínua do sensor
  int sensorValue = digitalRead(pirPin);

  // Detecta a transição de LOW para HIGH (movimento detectado)
  if (sensorValue == HIGH && lastSensorState == LOW) {
    Serial.println("Movimento detectado! Enviando dados...");
    enviarDados(1);
  }
  // Se o sensor voltar para LOW, atualiza sem enviar dados
  else if (sensorValue == LOW && lastSensorState == HIGH) {
    Serial.println("Sem movimento.");
  }

  lastSensorState = sensorValue;

  // Verificação periódica do status do Wi-Fi a cada 10 segundos
  static unsigned long lastCheck = 0;
  if (millis() - lastCheck >= 10000) {
    Serial.println("\n=== Status do Sistema ===");
    Serial.println("Uptime: " + String(millis() / 1000) + " segundos");

    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("WiFi conectado. IP: " + WiFi.localIP().toString());
      Serial.println("Força do sinal: " + String(WiFi.RSSI()) + " dBm");
    } else {
      Serial.println("WiFi desconectado - Tentando reconectar...");
      WiFi.reconnect();
    }
    lastCheck = millis();
  }

  delay(100);
}

