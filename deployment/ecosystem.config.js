module.exports = {
  "apps": [
    {
      "name": "cora-redis",
      "script": "redis-server",
      "instances": 1,
      "env": {
        "NODE_ENV": "production"
      }
    }
  ]
}