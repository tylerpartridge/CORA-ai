module.exports = {
  apps: [{
    name: cora,
    script: /usr/local/bin/uvicorn,
    args: app:app --host 0.0.0.0 --port 8000,
    cwd: /var/www/cora,
    interpreter: none,
    env: {
      PYTHONPATH: /var/www/cora
    }
  }]
}
