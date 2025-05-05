# **llm-forge**

**llm-forge** is a platform designed to rapidly evaluate and deploy large language models (LLMs), support fine-tuning and Retrieval-Augmented Generation (RAG) workflows, host specialized domain-specific models, and offer user-friendly abstractions for building agentic workflows. The aim is to make cutting-edge LLM capabilities accessible—even to users without deep machine learning expertise.

## **Core Features**
1. **Rapid LLM Deployment**: Evaluate and deploy newly released LLMs within 24 hours.
2. **Fine-Tuning & RAG Infrastructure**: Customize models with fine-tuning and RAG workflows using user-provided or local data.
3. **Specialized Model Hosting**: Deploy and manage domain-specific models (e.g., coding, legal, medical).
4. **Agentic Workflow Abstraction**: Create multi-step, goal-driven workflows using an intuitive visual or declarative interface.

---

## **Getting Started**

### **Requirements**
- [Node.js](https://nodejs.org/en/)
- [Docker](https://www.docker.com/)

### **Running the Platform**
Navigate to the project root directory and run:

```bash
docker-compose up --build -d
```

Once running, access the frontend at:
👉 http://localhost:80

### **Stopping the Platform**
To shut down all services:
```bash
docker-compose down
```

## Project Status

🚧 **This project is under active development.**

Currently, only the basic LLM evaluation and chat interface are functional. Additional capabilities—including fine-tuning, RAG pipelines, and the agentic workflow builder—are in progress.

