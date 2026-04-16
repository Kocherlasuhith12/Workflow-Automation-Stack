echo "⏳ Waiting for Restate admin API to be ready..."
sleep 5

echo "📝 Registering restate-service with Restate..."
curl -s -X POST http://localhost:9070/deployments \
  -H "Content-Type: application/json" \
  -d '{"uri": "http://restate-service:9080"}' \
  | python3 -m json.tool

echo ""
echo "✅ Done! Your greeter service is now registered."
echo "   You can test it with:"
echo "   curl -X POST http://localhost:8081/greeter/greet -H 'Content-Type: application/json' -d '\"World\"'"