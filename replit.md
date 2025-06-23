# Family Chore Tracker - Technical Documentation

## Overview

The Family Chore Tracker is a web-based application built with Flask that helps families manage household chores, track earnings, set goals, and monitor behavior. The application supports multiple user roles (parents and children) and provides features like time-based earnings calculation, streak tracking, and progress visualization.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python 3.11)
- **Web Server**: Gunicorn for production deployment
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Authentication**: Flask-Login with session-based authentication
- **Password Security**: Werkzeug password hashing

### Frontend Architecture
- **UI Framework**: Bootstrap 5 with dark theme
- **JavaScript Libraries**: 
  - FullCalendar for calendar functionality
  - Chart.js for data visualization
  - Custom JavaScript modules for feature-specific interactions
- **Icons**: Font Awesome 6.1.1
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Database Architecture
- **Primary Database**: PostgreSQL 15
- **Connection Management**: SQLAlchemy with connection pooling
- **Migration Strategy**: SQLAlchemy-based table creation and initialization

## Key Components

### Data Models
1. **User Model**: Handles both parent and child accounts with role-based permissions
2. **Family Model**: Groups users together with shared settings (hourly rate, family name)
3. **Chore Model**: Defines household tasks with time estimates and assignments
4. **ChoreCompletion Model**: Records when chores are completed with time tracking
5. **Goal Model**: Manages savings goals for individuals and families
6. **BehaviorRecord Model**: Tracks positive/negative behavior adjustments

### Core Features
1. **Chore Management**: Create, assign, and track household chores
2. **Time-Based Earnings**: Calculate payments based on time spent ($10/hour default)
3. **Daily Streak System**: Reward consistent completion of daily tasks
4. **Goal Tracking**: Set and monitor progress toward savings objectives
5. **Behavior Tracking**: Record positive/negative behavior impacts
6. **Calendar View**: Visual timeline of activities and completions
7. **Dashboard**: Role-specific views showing relevant metrics and progress

### User Interface Modules
- **Dashboard**: Central hub showing earnings, recent activities, and quick actions
- **Chores**: Management interface for creating and tracking chores
- **Goals**: Progress tracking for individual and family savings goals
- **Behavior**: Recording and monitoring behavior adjustments
- **Calendar**: Timeline view of all family activities
- **Settings**: Family configuration and user management

## Data Flow

### Authentication Flow
1. User login via username/password
2. Flask-Login manages session persistence
3. Role-based access control determines available features
4. Parents have full access; children have limited view/interaction capabilities

### Chore Completion Flow
1. Parent assigns chore to child with estimated time
2. Child marks chore as started/completed
3. System calculates earnings based on time spent and hourly rate
4. Completion is recorded with timestamp and earnings
5. Dashboard and calendar views are updated

### Goal Progress Flow
1. Goals are created with target amounts and deadlines
2. Earnings from chores automatically contribute to goal progress
3. Progress is visualized with charts and progress bars
4. Notifications and celebrations when goals are achieved

## External Dependencies

### Python Packages
- **flask**: Web framework
- **flask-sqlalchemy**: Database ORM
- **flask-login**: Authentication management
- **psycopg2-binary**: PostgreSQL adapter
- **gunicorn**: WSGI HTTP server
- **werkzeug**: WSGI utilities and security functions
- **email-validator**: Email validation support

### Frontend Libraries (CDN)
- **Bootstrap 5**: UI framework with dark theme
- **FullCalendar 5.10.0**: Calendar functionality
- **Font Awesome 6.1.1**: Icon library
- **Chart.js**: Data visualization (referenced but not fully implemented)

### Infrastructure Dependencies
- **PostgreSQL 15**: Primary database
- **Docker & Docker Compose**: Containerization and orchestration
- **Nginx/Reverse Proxy**: For production deployments (optional)

## Deployment Strategy

### Development Environment
- Direct Python execution with Flask development server
- SQLite or PostgreSQL for local development
- Environment variables for configuration

### Production Deployment
- **Containerized Deployment**: Docker containers with docker-compose
- **Multi-container Setup**: Separate containers for web application and database
- **Process Management**: Gunicorn with multiple workers
- **Data Persistence**: Docker volumes for database storage
- **Environment Configuration**: Environment variables for secrets and database connections

### Raspberry Pi Deployment
- Optimized for ARM64 architecture
- Docker Compose configuration for easy setup
- Initialization script for automated deployment
- Local network access with port forwarding

### Configuration Management
- Environment variables for sensitive data (database passwords, session secrets)
- JSON configuration files for business logic (daily chores, streak bonuses)
- Separate development and production configurations

## Changelog
- June 23, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.

## Known Issues and Considerations

### Current Implementation Status
- Application has syntax errors in app.py that need to be resolved
- Template rendering issues with undefined 'now' function
- Incomplete model definitions and route implementations
- Some JavaScript modules reference Chart.js but it's not included in dependencies

### Database Considerations
- Currently configured for PostgreSQL but can be adapted for other databases
- Connection pooling and retry logic implemented for reliability
- Database initialization includes sample data creation

### Security Considerations
- Password hashing implemented with Werkzeug
- Session-based authentication with configurable secret keys
- Role-based access control between parents and children
- Environment variable usage for sensitive configuration

### Performance Considerations
- Gunicorn configured with multiple workers for production
- Database connection pooling enabled
- Static asset serving optimized for production environments