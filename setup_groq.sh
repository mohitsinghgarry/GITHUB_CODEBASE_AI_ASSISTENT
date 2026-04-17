#!/bin/bash

# Setup script for switching to Groq LLM provider

echo "🚀 Setting up Groq for ultra-fast LLM responses"
echo ""
echo "================================================"
echo ""

# Check if backend/.env exists
if [ ! -f "backend/.env" ]; then
    echo "❌ backend/.env not found!"
    echo "Creating from backend/.env.example..."
    cp backend/.env.example backend/.env
fi

echo "📝 Please enter your Groq API key:"
echo "   (Get it from https://console.groq.com/)"
echo ""
read -p "Groq API Key: " GROQ_API_KEY

if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ No API key provided. Exiting."
    exit 1
fi

echo ""
echo "✅ Adding Groq configuration to backend/.env..."

# Add or update LLM_PROVIDER
if grep -q "^LLM_PROVIDER=" backend/.env; then
    sed -i.bak "s/^LLM_PROVIDER=.*/LLM_PROVIDER=groq/" backend/.env
else
    echo "" >> backend/.env
    echo "# LLM Provider Configuration" >> backend/.env
    echo "LLM_PROVIDER=groq" >> backend/.env
fi

# Add or update GROQ_API_KEY
if grep -q "^GROQ_API_KEY=" backend/.env; then
    sed -i.bak "s/^GROQ_API_KEY=.*/GROQ_API_KEY=$GROQ_API_KEY/" backend/.env
else
    echo "GROQ_API_KEY=$GROQ_API_KEY" >> backend/.env
fi

# Add or update GROQ_MODEL
if grep -q "^GROQ_MODEL=" backend/.env; then
    sed -i.bak "s/^GROQ_MODEL=.*/GROQ_MODEL=llama-3.3-70b-versatile/" backend/.env
else
    echo "GROQ_MODEL=llama-3.3-70b-versatile" >> backend/.env
fi

# Clean up backup files
rm -f backend/.env.bak

echo ""
echo "✅ Groq configuration added successfully!"
echo ""
echo "================================================"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Stop the backend server (Ctrl+C in Terminal 5)"
echo ""
echo "2. Restart the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "3. Test the chat at http://localhost:3000/chat"
echo ""
echo "Expected improvements:"
echo "  ⚡ Response time: 1-3 seconds (vs 30-60 seconds)"
echo "  ⚡ Streaming: Smooth and fast"
echo "  ⚡ Quality: Better responses with 70B model"
echo ""
echo "================================================"
