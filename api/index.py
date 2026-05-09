# Vercel Serverless Function Entry Point
from mangum import Mangum
from app.main import app

handler = Mangum(app, lifespan="on")
