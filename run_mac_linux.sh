#!/usr/bin/env bash
echo "Starting IshaaraBol server on http://localhost:8080 ..."
echo "Camera allow karne ke liye Chrome/Edge use karein."

if [ -z "$FIREWORKS_API_KEY" ]; then
  echo ""
  echo "NOTE: FIREWORKS_API_KEY set nahi hai — server.py mein already ek"
  echo "default key maujood hai, isliye AI Assistant abhi bhi Fireworks se"
  echo "jawab dega. Apni khud ki key use karne ke liye:"
  echo "  export FIREWORKS_API_KEY=fw_your_key_here"
  echo ""
fi

python3 server.py
