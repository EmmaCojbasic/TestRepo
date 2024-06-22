const mqtt = require('mqtt');

const qos = 2;
const mqttAddress = 'tcp://localhost:1883';
const clientId = 'serial-reader';
const username = 'serial-reader';
const password = 'serial-reader';
const topic = 'serial-reader/data';

const mqttClient = mqtt.connect(mqttAddress, {
    clientId,
    connectTimeout: 4000,
    username: username,
    password: password,
    reconnectPeriod: 1000
});

function parseAndPublishData(data) {
    console.log(`Data received: ${data}`);
    const values = data.split(", ").map(val => parseFloat(val.trim()));
    const jsonObject = {
        temperature: values[0],
        pressure: values[1],
        humidity: values[2]
    };
    mqttClient.publish(topic, JSON.stringify(jsonObject), { qos }, error => {
        if (error) {
            console.error('ERROR: ', error);
        }
    });
}

// Simulate sending and receiving data
const dataToSend = '25.3, 1013.2, 45.6'; // Example data string to send
while (true) {
    parseAndPublishData(dataToSend);
}
