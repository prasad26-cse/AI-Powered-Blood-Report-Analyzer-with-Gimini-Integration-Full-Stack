# Blood Test Analyzer AI - Improved Version

A comprehensive AI-powered blood test analysis system with enhanced performance, security, and reliability.

## 🚀 Features

- **AI-Powered Analysis**: Uses Google Gemini AI for intelligent blood test interpretation
- **Fast PDF Processing**: Optimized PDF text extraction with fallback mechanisms
- **Real-time Processing**: Asynchronous task processing with Celery
- **Modern Web Interface**: React-based frontend with responsive design
- **Secure Authentication**: JWT-based authentication with password hashing
- **Performance Monitoring**: Built-in performance optimization and monitoring
- **Database Flexibility**: Support for both MySQL and SQLite
- **Caching**: Redis-based caching for improved performance
- **Error Handling**: Comprehensive error handling and recovery

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Redis (optional, can use memory broker)
- MySQL (optional, SQLite fallback available)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd blood-test-analyser-debug
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up Frontend
```bash
cd frontend
npm install
cd ..
```

### 4. Configure Environment
```bash
# Copy environment template
cp env.template .env

# Edit .env file with your configuration
# Required variables:
# - SECRET_KEY: Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
# - GEMINI_API_KEY: Get from https://makersuite.google.com/app/apikey
```

### 5. Database Setup
```bash
# For MySQL (recommended for production):
# Create database and configure in .env

# For SQLite (development):
# No additional setup required, will be created automatically
```

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)
```bash
python start_improved.py
```

This script will:
- Check all dependencies
- Validate environment configuration
- Run performance optimization
- Start all services automatically
- Monitor services and restart if needed

### Option 2: Manual Startup

#### 1. Start Redis (if using)
```bash
redis-server
```

#### 2. Start Celery Worker
```bash
celery -A celery_app worker --loglevel=info
```

#### 3. Start Backend
```bash
python main_optimized.py
```

#### 4. Start Frontend
```bash
cd frontend
npm start
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Performance Monitor**: http://localhost:8000/api/performance

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `DB_USER` | Database username | `root` |
| `DB_PASSWORD` | Database password | `` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `3306` |
| `DB_NAME` | Database name | `bloodreport_ai` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/0` |

### Performance Tuning

The system automatically optimizes settings based on your hardware:

- **CPU**: Adjusts worker concurrency based on CPU cores
- **Memory**: Optimizes chunk sizes and worker limits
- **Storage**: Monitors disk usage and provides warnings

Run performance optimization manually:
```bash
python performance_optimizer.py
```

## 📊 Performance Monitoring

### Built-in Monitoring
- Real-time CPU and memory usage tracking
- Automatic performance warnings
- Service health monitoring
- Automatic service restart on failure

### Performance Reports
Performance reports are automatically generated and saved as JSON files:
- `performance_report_YYYYMMDD_HHMMSS.json`

### Monitoring Endpoints
- `GET /health` - Basic health check
- `GET /api/performance` - Detailed performance metrics

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt password hashing
- **CORS Protection**: Configurable CORS settings
- **Rate Limiting**: Built-in rate limiting (configurable)
- **Input Validation**: Comprehensive input validation
- **SQL Injection Protection**: Parameterized queries

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 2. Database Connection Issues
```bash
# Check database configuration in .env
# For SQLite fallback, ensure write permissions
```

#### 3. Redis Connection Issues
```bash
# Check if Redis is running
redis-cli ping

# If not running, start Redis or use memory broker
# Set CELERY_BROKER_URL=memory:// in .env
```

#### 4. Frontend Build Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### 5. PDF Processing Issues
```bash
# Check if PDF files are valid
# Ensure sufficient disk space
# Check file permissions
```

### Performance Issues

#### High CPU Usage
- Reduce `max_workers` in PDF processing
- Lower Celery worker concurrency
- Check for memory leaks

#### High Memory Usage
- Implement memory cleanup in PDF processing
- Reduce chunk sizes
- Monitor for memory leaks

#### Slow Processing
- Check network connectivity to AI services
- Optimize database queries
- Enable caching

### Logs and Debugging

#### Enable Debug Mode
Set `DEBUG=True` in `.env` for detailed logging.

#### View Logs
- Backend logs: Check console output
- Frontend logs: Check browser console
- Celery logs: Check Celery worker output
- Startup logs: `startup.log`

## 🧪 Testing

### Run All Tests
```bash
# Backend tests
python -m pytest test_*.py

# Frontend tests
cd frontend
npm test
```

### Individual Tests
```bash
# Test Gemini AI connection
python test_gemini.py

# Test Celery functionality
python test_celery_gemini.py

# Test PDF processing
python test_analysis.py
```

## 📈 Performance Benchmarks

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4GB | 8GB+ |
| Storage | 10GB | 50GB+ |
| Network | 10Mbps | 100Mbps+ |

### Performance Metrics

- **PDF Processing**: 2-5 seconds per page
- **AI Analysis**: 10-30 seconds per report
- **Concurrent Users**: 10-50 (depending on hardware)
- **Database Queries**: <100ms average

## 🔄 Updates and Maintenance

### Regular Maintenance
1. **Database Cleanup**: Remove old reports periodically
2. **Log Rotation**: Rotate log files to prevent disk space issues
3. **Performance Monitoring**: Run performance optimization regularly
4. **Security Updates**: Keep dependencies updated

### Backup Strategy
- **Database**: Regular database backups
- **Uploaded Files**: Backup `data/` directory
- **Configuration**: Backup `.env` file

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Check the API documentation at `/docs`
4. Create an issue with detailed error information

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Mobile app
- [ ] Integration with EHR systems
- [ ] Advanced AI models
- [ ] Real-time collaboration features 