# Smart Assist: Your 24/7 AI Business Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Issues](https://img.shields.io/github/issues/maruthireddy432/AI-Chatbot)](https://github.com/maruthireddy432/AI-Chatbot/issues)
[![Forks](https://img.shields.io/github/forks/maruthireddy432/AI-Chatbot)](https://github.com/maruthireddy432/AI-Chatbot/network)
[![Stars](https://img.shields.io/github/stars/maruthireddy432/AI-Chatbot)](https://github.com/maruthireddy432/AI-Chatbot/stargazers)

A lightweight, easy-to-integrate chatbot designed to help businesses automate customer interactions, capture leads, and provide instant support 24/7.

<img width="908" height="986" alt="chatbot" src="https://github.com/user-attachments/assets/fc98638f-efaf-467a-a593-def1fa7ee0ca" />.

## The Problem

Running a business is demanding. Owners and small teams are often overwhelmed, wearing multiple hats—including sales, marketing, and 24/7 customer support. Valuable time is lost answering the same repetitive questions ("What are your hours?", "Do you offer X?"), and potential leads are missed simply because they come in after business hours.

Enterprise-level automation tools are often too complex, expensive, or bloated for the needs of a growing business.

## The Solution

This chatbot project provides a simple, powerful, and affordable solution. It acts as a digital assistant on your website, handling the frontline of customer communication.

It's designed to free up business owners from the "noise" and repetitive tasks, allowing them to focus on high-value work: building relationships, closing sales, and growing their business.

## ✨ Key Features

* **📈 24/7 Lead Capture:** Never miss a lead again. The bot can qualify visitors and collect their contact information (name, email, phone) even when you're offline.
* **❓ Instant FAQ Answers:** Provide immediate answers to common questions about your hours, services, location, and more.
* **🗓️ Appointment Booking:** Integrates with [Your Calendar System, e.g., Calendly] to book meetings or appointments directly within the chat.
* **🚀 Lightweight & Easy to Embed:** Add the bot to any website with a simple copy-paste JavaScript snippet.
* **💬 Customizable Conversations:** Easily define and update conversation flows, questions, and answers in a simple JSON or admin panel [adjust as needed].
* **🔔 Real-time Notifications:** Get instantly notified via [Email/Slack/Dashboard] when a new lead is captured.

## 💻 Tech Stack

This project is built with a modern, scalable stack:

* **Frontend (Chat Widget):** [ React, Plain JavaScript/HTML/CSS]
* **Backend (Server):** [ Node.js with Express, Python with FastAPI]
* **NLP / Brain:** [ LangChain, Groq LLM's]
* **Database:** [MY SQL]
* **Deployment:** [ Docker]

## 🚀 Getting Started

Follow these instructions to get a local copy up and running for development and testing.

### Prerequisites

* [Node.js (v18.x or higher)](https://nodejs.org/)
* [Python (v3.10.x or higher)](https://www.python.org/)
* [MY SQL Database](https://www.postgresql.org/)
* [Git](https://git-scm.com/)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/maruthireddy432/AI-Chatbot.git](https://github.com/maruthireddy432/AI-Chatbot.git)
    cd your-repo-name
    ```

2.  **Set up the Backend:**
    ```bash
    cd server
    # Install dependencies
    npm install 
    # or
    pip install -r requirements.txt
    ```

3.  **Set up the Frontend (Chat Widget):**
    ```bash
    cd client
    # Install dependencies
    npm install
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the `server` directory. Copy the contents of `.env.example` and fill in your details:
    ```.env
    DATABASE_URL="postgresql://user:password@localhost:5432/your-db-name"
    API_SECRET_KEY="your_secret_key"
    DIALOGFLOW_PROJECT_ID="your_project_id"
    # etc...
    ```

5.  **Run the application:**
    * **Start the backend server:**
        ```bash
        # In the /server directory
        npm start
        ```
    * **Start the frontend development server:**
        ```bash
        # In the /client directory
        npm run dev
        ```

## ⚙️ Usage & Configuration

### Embedding the Bot on Your Website

Once the server is running, you can embed the chatbot on any HTML page by adding the following snippet before the closing `</body>` tag:

```html
<script src="[https://your-server-domain.com/widget.js](https://your-server-domain.com/widget.js)" defer></script>
