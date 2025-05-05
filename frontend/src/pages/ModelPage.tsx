// src/pages/ModelPage.tsx
import React, { useState, useEffect, useCallback } from 'react';
import './ModelPage.css'; 
import axios from 'axios';

const API_BASE_URL = '/api'; // Using relative path for proxy

// --- Interfaces (Define data structures) ---
interface ModelInfo {
    id: string;          // Unique identifier (e.g., 'huggingface/google/gemma-7b-it', 'openai/gpt-4')
    name: string;        // User-friendly name (e.g., 'Gemma 7B Instruct', 'GPT-4')
    source?: string;      // Optional: Where it comes from (e.g., 'Hugging Face', 'OpenAI', 'Local')
    deployed?: boolean;   // Is it currently active/deployed in the forge?
}

interface EvalConfig {
    temperature: number;
    maxTokens: number;
    // Add other relevant parameters (top_p, top_k etc.) if needed
}

function ModelPage() {
    // --- State ---
    const [models, setModels] = useState<ModelInfo[]>([]);
    const [deployedModels, setDeployedModels] = useState<ModelInfo[]>([]);   // Models currently active
    const [selectedModel, setSelectedModel] = useState<string>('');     // ID of the model chosen for evaluation
    const [evaluationPrompt, setEvaluationPrompt] = useState<string>('');
    const [evaluationResponse, setEvaluationResponse] = useState<string>('');
    const [evalConfig, setEvalConfig] = useState<EvalConfig>({ temperature: 0.7, maxTokens: 512 });
    const [isLoadingEval, setIsLoadingEval] = useState<boolean>(false);
    const [isLoadingDeploy, setIsLoadingDeploy] = useState<boolean>(false);
    const [statusMessage, setStatusMessage] = useState<string>(''); // For feedback
    const [error, setError] = useState<string | null>(null);

    // --- Fetch Initial Data ---
    useEffect(() => {
        axios.get<{ id: string; name: string }[]>(`${API_BASE_URL}/models`)
          .then(response => {
            setModels(response.data);
            // Select the first model by default if available
            if (response.data.length > 0) {
              setSelectedModel(response.data[0].id);
            }
          })
          .catch(err => {
            console.error("Error fetching models:", err);
            setError('Failed to load models. Is the backend running?');
          });
      }, []);


    useEffect(() => {
        // TODO: Replace with actual API calls to your backend
        const fetchModels = async () => {
            try {
                setStatusMessage('Fetching model lists...');
                // Placeholder/Example Data
                setDeployedModels(models.filter(m => m.deployed));
                if (models.length > 0) {
                   // Select the first non-deployed model for evaluation by default, or just the first one
                   const firstEvalCandidate = models.find(m => !m.deployed) || models[0];
                   if (firstEvalCandidate) {
                       setSelectedModel(firstEvalCandidate.id);
                   }
                }
                setStatusMessage(''); // Clear status
            } catch (error) {
                console.error("Error fetching models:", error);
                setStatusMessage('Error fetching models.');
            }
        };

        fetchModels();
    }, []); // Run once on mount

    // --- Event Handlers ---
    const handleModelSelectChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedModel(event.target.value);
        setEvaluationResponse(''); // Clear previous response on model change
        setEvaluationPrompt('');   // Clear prompt
        setStatusMessage('');
    };

    const handleConfigChange = (param: keyof EvalConfig, value: number | string) => {
        setEvalConfig(prev => ({
            ...prev,
            [param]: typeof prev[param] === 'number' ? parseFloat(value as string) : value,
        }));
    };

    const handleEvaluate = useCallback(async () => {
        if (!selectedModel || !evaluationPrompt.trim()) {
            setStatusMessage('Please select a model and enter a prompt.');
            return;
        }
        setIsLoadingEval(true);
        setEvaluationResponse('');
        setStatusMessage(`Evaluating ${selectedModel}...`);

        try {
            // --- TODO: Replace with actual API call to backend ---
            console.log("Sending Evaluation Request:", {
                modelId: selectedModel,
                prompt: evaluationPrompt,
                config: evalConfig,
            });
            // Example: const response = await fetch('/api/evaluate-model', { ... });
            // const data = await response.json(); // Assuming backend returns { response: "..." }

            // --- Simulated Response ---
            await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate network delay
            const simulatedResponse = `Simulated response from ${selectedModel} for prompt "${evaluationPrompt}" with temp ${evalConfig.temperature.toFixed(1)}. Lorem ipsum dolor sit amet.`;
            // --- End Simulation ---

            setEvaluationResponse(simulatedResponse); // Replace with data.response
            setStatusMessage('Evaluation complete.');

        } catch (error) {
            console.error("Error during evaluation:", error);
            setStatusMessage(`Error evaluating ${selectedModel}.`);
            setEvaluationResponse('Failed to get response.');
        } finally {
            setIsLoadingEval(false);
        }
    }, [selectedModel, evaluationPrompt, evalConfig]); // Dependencies

    const handleDeploy = useCallback(async (modelIdToDeploy: string) => {
        if (!modelIdToDeploy) return;

        const modelToDeploy = models.find(m => m.id === modelIdToDeploy);
        if (!modelToDeploy) {
             setStatusMessage(`Model with ID ${modelIdToDeploy} not found.`);
             return;
        }
        if (modelToDeploy.deployed) {
            setStatusMessage(`${modelToDeploy.name} is already deployed.`);
            return; // Or implement undeploy logic here if needed
        }

        setIsLoadingDeploy(true);
        setStatusMessage(`Deploying ${modelToDeploy.name}...`);

        try {
            // --- TODO: Replace with actual API call to backend ---
            console.log("Sending Deployment Request:", { modelId: modelIdToDeploy });
            // Example: const response = await fetch('/api/deploy-model', { method: 'POST', body: JSON.stringify({ modelId: modelIdToDeploy }) });
            // if (!response.ok) throw new Error('Deployment failed');

            // --- Simulate Success ---
            await new Promise(resolve => setTimeout(resolve, 2000));
            // --- End Simulation ---

            // Update state optimistically or after confirmation from backend
            setDeployedModels(prev => [...prev, { ...modelToDeploy, deployed: true }]);
            setModels(prev => prev.map(m => m.id === modelIdToDeploy ? { ...m, deployed: true } : m));
            setStatusMessage(`${modelToDeploy.name} deployed successfully.`);

        } catch (error) {
            console.error("Error deploying model:", error);
            setStatusMessage(`Error deploying ${modelToDeploy.name}.`);
        } finally {
            setIsLoadingDeploy(false);
        }

    }, [models]); // Dependency

    // --- Render ---
    const selectedModelInfo = models.find(m => m.id === selectedModel);

    return (
        <div className="model-eval-page">
            <h1>LLM Evaluation & Deployment</h1>
            
            {error && <p className="error-message">Error: {error}</p>}

            {statusMessage && <p className="status-message">{statusMessage}</p>}

            <div className="eval-layout">
                {/* Left Side: Selection & Evaluation */}
                <section className="eval-section">
                    <h2>Evaluate Model</h2>

                    <div className="config-item">
                        <label htmlFor="model-select-eval">Select Model:</label>
                        <select
                            id="model-select-eval"
                            value={selectedModel}
                            onChange={handleModelSelectChange}
                            disabled={isLoadingEval || isLoadingDeploy}
                        >
                            <option value="" disabled>-- Choose a model --</option>
                            {models.map(model => (
                                <option key={model.id} value={model.id} disabled={model.deployed}>
                                     {model.name} ({model.source}) {model.deployed ? '[Deployed]' : ''}
                                </option>
                            ))}
                        </select>
                         {/* Add input for custom model ID/endpoint if needed */}
                    </div>

                    {selectedModelInfo && !selectedModelInfo.deployed && (
                         <>
                             <div className="config-item">
                                 <label htmlFor="eval-prompt">Test Prompt:</label>
                                 <textarea
                                     id="eval-prompt"
                                     rows={4}
                                     value={evaluationPrompt}
                                     onChange={(e) => setEvaluationPrompt(e.target.value)}
                                     placeholder={`Send a prompt to ${selectedModelInfo?.name || 'the selected model'}...`}
                                     disabled={isLoadingEval}
                                 />
                             </div>

                            {/* Evaluation Configuration */}
                            <fieldset className="eval-config">
                                 <legend>Evaluation Config</legend>
                                 <div className="config-item-inline">
                                     <label htmlFor="eval-temp">Temperature:</label>
                                     <input
                                         type="range"
                                         id="eval-temp"
                                         min="0.0" max="2.0" step="0.1"
                                         value={evalConfig.temperature}
                                         onChange={(e) => handleConfigChange('temperature', e.target.value)}
                                         disabled={isLoadingEval}
                                     />
                                     <span>{evalConfig.temperature.toFixed(1)}</span>
                                 </div>
                                 <div className="config-item-inline">
                                     <label htmlFor="eval-maxTokens">Max Tokens:</label>
                                     <input
                                         type="number"
                                         id="eval-maxTokens"
                                         min="1" step="1"
                                         value={evalConfig.maxTokens}
                                         onChange={(e) => handleConfigChange('maxTokens', e.target.value)}
                                         disabled={isLoadingEval}
                                         style={{width: '80px'}}
                                     />
                                 </div>
                                 {/* Add more config inputs */}
                            </fieldset>

                            <button onClick={handleEvaluate} disabled={isLoadingEval || !evaluationPrompt.trim()}>
                                 {isLoadingEval ? 'Evaluating...' : 'Run Evaluation'}
                             </button>

                            <div className="eval-response">
                                 <h3>Response:</h3>
                                 {isLoadingEval && <p>Loading...</p>}
                                 <pre>{evaluationResponse || (!isLoadingEval ? '(No response yet)' : '')}</pre>
                            </div>

                            {/* Deploy Button for the currently selected/evaluated model */}
                            {!selectedModelInfo.deployed && evaluationResponse && ( // Show deploy after successful eval? Or always?
                                <button
                                    onClick={() => handleDeploy(selectedModel)}
                                    disabled={isLoadingDeploy || isLoadingEval || selectedModelInfo.deployed}
                                    className="deploy-button"
                                    style={{marginTop: '20px'}}
                                >
                                     {isLoadingDeploy ? 'Deploying...' : `Deploy ${selectedModelInfo.name}`}
                                </button>
                            )}
                         </>
                    )}
                    {selectedModelInfo?.deployed && (
                        <p style={{marginTop: '20px', fontWeight: 'bold'}}>
                            {selectedModelInfo.name} is already deployed.
                        </p>
                    )}

                </section>

                {/* Right Side: Deployed Models List */}
                <section className="deployed-section">
                    <h2>Deployed Models</h2>
                    {deployedModels.length === 0 ? (
                        <p>No models are currently deployed.</p>
                    ) : (
                        <ul className="deployed-list">
                            {deployedModels.map(model => (
                                <li key={model.id}>
                                    <strong>{model.name}</strong> ({model.source})
                                    {/* Optional: Add undeploy button or status indicator */}
                                    {/* <button onClick={() => handleUndeploy(model.id)} disabled={isLoadingDeploy}>Undeploy</button> */}
                                </li>
                            ))}
                        </ul>
                    )}
                    <p style={{marginTop: '15px', fontSize: '0.9em'}}>
                        Deployed models are available for use in Chat and other features.
                    </p>
                </section>
            </div>
        </div>
    );
}

export default ModelPage;