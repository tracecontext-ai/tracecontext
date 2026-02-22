import axios from 'axios';

export const statusCommand = async () => {
    try {
        const response = await axios.get('http://localhost:8000/');
        console.log('Orchestrator Status:', response.data.status);
    } catch (error) {
        console.error('Orchestrator is offline. Start it with "python orchestrator/main.py"');
    }
};
