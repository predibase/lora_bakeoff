/**
 * Author: Wael Abid
 * 
 * Sample command:
 * > k6 run --env CONCURRENT_REQUESTS=2 \
 *   --env NUM_INPUT_WORDS_LOWER_BOUND=90 \
 *   --env NUM_INPUT_WORDS_UPPER_BOUND=110 \
 *   --env MAX_NEW_TOKENS_LOWER_BOUND=90 \
 *   --env MAX_NEW_TOKENS_UPPER_BOUND=110 \
 *   --env SERVING_GATEWAY=serving.app.predibase.com \
 *   --env TENANT=fd6c79 \
 *   --env DEPLOYMENT_NAME=llama-2-7b-chat \
 *   --env AUTH_TOKEN=pb_jcN0OPMdWt-yrgIg0aBnTA \
 *   load_test.js
 * 
 * The script will establish a connection with LLMs and reuse that connection for all queries, so the TLS handshake 
 * latency will be amortized across all the numbers reported.
 *  
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.1.0/index.js';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';


const concurrentRequests = __ENV.CONCURRENT_REQUESTS ? parseInt(__ENV.CONCURRENT_REQUESTS, 10) : 1;
export let options = {
    setupTimeout: '15m',
    summaryTimeUnit: 'ms',
    stages: [
        { duration: '1s', target: concurrentRequests }, // Use getTarget function to set target
        { duration: '60s', target: concurrentRequests },
    ],
};

// Read word list from an external file once
let wordList = [];
try {
    // const fileContent = readFileSync('text.txt', 'utf8');
    const fileContent = open('./text.txt');
    wordList = fileContent.split(' ');
} catch (error) {
    console.error(`Error reading word list file: ${error}`);
}

function getRandomText(words, min, max) {
    const numberOfWords = randomIntBetween(min, max); // Random number of words
    let randomText = [];
    for (let i = 0; i < numberOfWords; i++) {
        randomText.push(words[Math.floor(Math.random() * words.length)]);
    }
    return randomText.join(' ');
}

export function setup() {
    const startTime = new Date().getTime();
    const duration = 15 * 60 * 1000; // 15 minutes in milliseconds
    const interval = 10; // Interval of 10 seconds

    // Construct the health endpoint URL
    const servingGateway = __ENV.SERVING_GATEWAY;
    const tenant = __ENV.TENANT;
    const deploymentName = __ENV.DEPLOYMENT_NAME;
    const healthUrl = `https://${servingGateway}/${tenant}/deployments/v2/llms/${deploymentName}/health`;
    const generateStreamUrl = `https://${servingGateway}/${tenant}/deployments/v2/llms/${deploymentName}/generate_stream`;
    const params = {
        headers: {
            'Content-Type': 'application/json',
            // Read authorization token from environment variable
            'Authorization': `Bearer ${__ENV.AUTH_TOKEN}`,
        },
    };

    while (new Date().getTime() - startTime < duration) {
        // GET request to the `/health` endpoint
        const healthResponse = http.get(healthUrl, params);

        // Check the response status and abort the test if the response is not 200
        if (healthResponse.status !== 200) {
            console.error(`Health check ${healthUrl} failed with status: ${healthResponse.status}`);
        } else {
            console.info(`Health check succeeded`)
            const payload = JSON.stringify({
                inputs: "warmup",
                parameters: { max_new_tokens: 1, details: false }
            });
            const generateResponse = http.post(generateStreamUrl, payload, params);
            return generateResponse.status
        }
        sleep(interval);
    }
}

export default function () {
    // Random text between NUM_INPUT_WORDS_LOWER_BOUND and NUM_INPUT_WORDS_UPPER_BOUND words
    const minWords = __ENV.NUM_INPUT_WORDS_LOWER_BOUND ? parseInt(__ENV.NUM_INPUT_WORDS_LOWER_BOUND, 10) : 1;
    const maxWords = __ENV.NUM_INPUT_WORDS_UPPER_BOUND ? parseInt(__ENV.NUM_INPUT_WORDS_UPPER_BOUND, 10) : 20;
    const some_text = getRandomText(wordList, minWords, maxWords);

    // Random number between MAX_NEW_TOKENS_LOWER_BOUND and MAX_NEW_TOKENS_UPPER_BOUND
    const minNum = __ENV.MAX_NEW_TOKENS_LOWER_BOUND ? parseInt(__ENV.MAX_NEW_TOKENS_LOWER_BOUND, 10) : 90;
    const maxNum = __ENV.MAX_NEW_TOKENS_UPPER_BOUND ? parseInt(__ENV.MAX_NEW_TOKENS_UPPER_BOUND, 10) : 110;
    const some_number = randomIntBetween(minNum, maxNum);

    // Construct URL from environment variables
    const servingGateway = __ENV.SERVING_GATEWAY;
    const tenant = __ENV.TENANT;
    const deploymentName = __ENV.DEPLOYMENT_NAME;
    const url = `https://${servingGateway}/${tenant}/deployments/v2/llms/${deploymentName}/generate_stream`;

    const payload = JSON.stringify({
        inputs: some_text,
        parameters: { max_new_tokens: some_number, details: false }
    });
    const params = {
        headers: {
            'Content-Type': 'application/json',
            // Read authorization token from environment variable
            'Authorization': `Bearer ${__ENV.AUTH_TOKEN}`,
        },
    };

    const response = http.post(url, payload, params);

    check(response, {
        'is status 200': (r) => r.status === 200,
    });

    sleep(1);
}

export function handleSummary(data) {
    return {
        stdout: textSummary(data),
        'load-test-summary.json': JSON.stringify(data), // todo: modify path with unique path
    };
}
