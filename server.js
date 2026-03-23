const express = require('express');
const path = require('path');
const mongoose = require('mongoose');
const mysql = require('mysql2/promise');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// ================================
// DATABASE CONNECTION SETUP
// ================================

// MongoDB Configuration
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/taskvise';
const MONGO_CONFIG = {
  serverSelectionTimeoutMS: 5000,
  socketTimeoutMS: 45000,
};

// MySQL Configuration
const MYSQL_CONFIG = {
  host: process.env.MYSQL_HOST || 'localhost',
  user: process.env.MYSQL_USER || 'root',
  password: process.env.MYSQL_PASSWORD || 'root',
  database: process.env.MYSQL_DB || 'Taskvise',
  port: process.env.MYSQL_PORT || 3306,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
};

// Database Connection Objects
let mongoConnected = false;
let mysqlConnected = false;
let mongoConnection = null;
let mysqlPool = null;

// ================================
// MONGODB CONNECTION
// ================================

function initializeMongoConnection() {
  mongoose.connect(MONGO_URI, MONGO_CONFIG)
    .then(() => {
      mongoConnected = true;
      console.log('\n✅ MongoDB Connected Successfully');
      console.log('   URI:', MONGO_URI);
      console.log('   Database: taskvise');
      initializeMongoSchemas();
    })
    .catch((err) => {
      mongoConnected = false;
      console.error('\n❌ MongoDB Connection Failed');
      console.error('   Error:', err.message);
      console.error('   Attempting to reconnect in 5 seconds...\n');
      setTimeout(initializeMongoConnection, 5000);
    });
}

function initializeMongoSchemas() {
  const mongooseConnection = mongoose.connection;
  
  // Define schemas for all collections
  const genericSchema = new mongoose.Schema({}, { strict: false });
  
  mongoConnection = {
    users: mongoose.model('users', genericSchema, 'users'),
    employees: mongoose.model('employees', genericSchema, 'employees'),
    tasks: mongoose.model('tasks', genericSchema, 'tasks'),
    projects: mongoose.model('projects', genericSchema, 'projects'),
    companies: mongoose.model('companies', genericSchema, 'companies'),
  };
}

initializeMongoConnection();

// ================================
// MYSQL CONNECTION POOL
// ================================

async function initializeMysqlConnection() {
  try {
    mysqlPool = mysql.createPool(MYSQL_CONFIG);
    
    // Test connection
    const connection = await mysqlPool.getConnection();
    connection.release();
    
    mysqlConnected = true;
    console.log('\n✅ MySQL Connected Successfully');
    console.log('   Host:', MYSQL_CONFIG.host);
    console.log('   Port:', MYSQL_CONFIG.port);
    console.log('   Database:', MYSQL_CONFIG.database);
    console.log('   User:', MYSQL_CONFIG.user);
    
    await createMysqlTables();
  } catch (err) {
    mysqlConnected = false;
    console.error('\n❌ MySQL Connection Failed');
    console.error('   Error:', err.message);
    console.error('   Attempting to reconnect in 5 seconds...\n');
    setTimeout(initializeMysqlConnection, 5000);
  }
}

async function createMysqlTables() {
  const tables = [
    `CREATE TABLE IF NOT EXISTS users (
      id VARCHAR(36) PRIMARY KEY,
      username VARCHAR(255) UNIQUE,
      email VARCHAR(255) UNIQUE,
      password_hash VARCHAR(255),
      full_name VARCHAR(255),
      role VARCHAR(50),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      is_active BOOLEAN DEFAULT TRUE
    )`,
    
    `CREATE TABLE IF NOT EXISTS employees (
      id VARCHAR(36) PRIMARY KEY,
      name VARCHAR(255),
      email VARCHAR(255),
      position VARCHAR(255),
      department VARCHAR(255),
      join_date DATE,
      phone VARCHAR(20),
      skills TEXT,
      location VARCHAR(255),
      last_login TIMESTAMP,
      password_last_changed TIMESTAMP,
      avatar_url VARCHAR(255),
      productivity FLOAT
    )`,
    
    `CREATE TABLE IF NOT EXISTS tasks (
      id VARCHAR(36) PRIMARY KEY,
      title VARCHAR(255),
      description TEXT,
      status VARCHAR(50),
      assigned_to VARCHAR(36),
      project_id VARCHAR(36),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      due_date DATE,
      priority VARCHAR(50)
    )`,
    
    `CREATE TABLE IF NOT EXISTS projects (
      id VARCHAR(36) PRIMARY KEY,
      name VARCHAR(255),
      description TEXT,
      manager_id VARCHAR(36),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      status VARCHAR(50),
      team_size INT
    )`,
    
    `CREATE TABLE IF NOT EXISTS companies (
      id VARCHAR(36) PRIMARY KEY,
      name VARCHAR(255),
      industry VARCHAR(255),
      country VARCHAR(255),
      plan_type VARCHAR(50),
      total_users INT DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      is_active BOOLEAN DEFAULT TRUE
    )`
  ];
  
  try {
    for (const table of tables) {
      await mysqlPool.query(table);
    }
    console.log('   ✓ All tables created/verified');
  } catch (err) {
    console.error('   ⚠ Error creating tables:', err.message);
  }
}

initializeMysqlConnection();

// ================================
// MANAGER ENDPOINTS (Dashboard)
// ================================

app.get('/api/manager/employees', async (req, res) => {
  try {
    if (mongoConnected && mongoConnection) {
      const data = await mongoConnection.employees.find().lean();
      return res.json(data);
    }
    if (mysqlConnected && mysqlPool) {
      const [rows] = await mysqlPool.query('SELECT * FROM employees');
      return res.json(rows);
    }
    res.status(503).json({ error: 'No database available' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/manager/tasks', async (req, res) => {
  try {
    if (mongoConnected && mongoConnection) {
      const data = await mongoConnection.tasks.find().lean();
      return res.json(data);
    }
    if (mysqlConnected && mysqlPool) {
      const [rows] = await mysqlPool.query('SELECT * FROM tasks');
      return res.json(rows);
    }
    res.status(503).json({ error: 'No database available' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/manager/projects', async (req, res) => {
  try {
    if (mongoConnected && mongoConnection) {
      const data = await mongoConnection.projects.find().lean();
      return res.json(data);
    }
    if (mysqlConnected && mysqlPool) {
      const [rows] = await mysqlPool.query('SELECT * FROM projects');
      return res.json(rows);
    }
    res.status(503).json({ error: 'No database available' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/manager/stats', async (req, res) => {
  try {
    const counts = {};
    
    if (mongoConnected && mongoConnection) {
      counts.employees = await mongoConnection.employees.countDocuments();
      counts.projects = await mongoConnection.projects.countDocuments();
      counts.tasks = await mongoConnection.tasks.countDocuments();
      counts.tasks_completed = await mongoConnection.tasks.countDocuments({ status: 'completed' });
    } else if (mysqlConnected && mysqlPool) {
      const [empRows] = await mysqlPool.query('SELECT COUNT(*) as count FROM employees');
      const [projRows] = await mysqlPool.query('SELECT COUNT(*) as count FROM projects');
      const [taskRows] = await mysqlPool.query('SELECT COUNT(*) as count FROM tasks');
      const [complRows] = await mysqlPool.query("SELECT COUNT(*) as count FROM tasks WHERE status='completed'");
      counts.employees = empRows[0].count;
      counts.projects = projRows[0].count;
      counts.tasks = taskRows[0].count;
      counts.tasks_completed = complRows[0].count;
    }
    
    return res.json(counts);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ================================
// API ROUTES - GET ALL DATA
// ================================

app.get('/api/:model', async (req, res) => {
  const model = req.params.model;
  const validModels = ['users', 'employees', 'tasks', 'projects', 'companies'];
  
  if (!validModels.includes(model)) {
    return res.status(400).json({ error: 'Invalid model' });
  }

  try {
    // Try MongoDB first
    if (mongoConnected && mongoConnection) {
      const data = await mongoConnection[model].find().lean();
      return res.json({
        data,
        source: 'MongoDB',
        count: data.length
      });
    }
    
    // Fallback to MySQL
    if (mysqlConnected && mysqlPool) {
      const [rows] = await mysqlPool.query(`SELECT * FROM ${model}`);
      return res.json({
        data: rows,
        source: 'MySQL',
        count: rows.length
      });
    }
    
    res.status(503).json({ error: 'No database connection available' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ================================
// API ROUTES - GET BY ID
// ================================

app.get('/api/:model/:id', async (req, res) => {
  const { model, id } = req.params;
  const validModels = ['users', 'employees', 'tasks', 'projects', 'companies'];
  
  if (!validModels.includes(model)) {
    return res.status(400).json({ error: 'Invalid model' });
  }

  try {
    // Try MongoDB first
    if (mongoConnected && mongoConnection) {
      const data = await mongoConnection[model].findOne({ id: id }).lean();
      if (!data) {
        return res.status(404).json({ error: 'Document not found' });
      }
      return res.json({
        data,
        source: 'MongoDB'
      });
    }
    
    // Fallback to MySQL
    if (mysqlConnected && mysqlPool) {
      const [rows] = await mysqlPool.query(`SELECT * FROM ${model} WHERE id = ?`, [id]);
      if (rows.length === 0) {
        return res.status(404).json({ error: 'Record not found' });
      }
      return res.json({
        data: rows[0],
        source: 'MySQL'
      });
    }
    
    res.status(503).json({ error: 'No database connection available' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ================================
// API ROUTES - CREATE
// ================================

app.post('/api/:model', async (req, res) => {
  const model = req.params.model;
  const newData = req.body;
  const validModels = ['users', 'employees', 'tasks', 'projects', 'companies'];
  
  if (!validModels.includes(model)) {
    return res.status(400).json({ error: 'Invalid model' });
  }

  try {
    let savedData = newData;
    let savedSources = [];

    // Save to MongoDB
    if (mongoConnected && mongoConnection) {
      try {
        const document = new mongoConnection[model](newData);
        savedData = await document.save();
        savedSources.push('MongoDB');
      } catch (mongoErr) {
        console.error(`MongoDB save error for ${model}:`, mongoErr.message);
      }
    }

    // Save to MySQL
    if (mysqlConnected && mysqlPool) {
      try {
        const columns = Object.keys(newData);
        const values = Object.values(newData);
        const placeholders = columns.map(() => '?').join(',');
        
        await mysqlPool.query(
          `INSERT INTO ${model} (${columns.join(',')}) VALUES (${placeholders})`,
          values
        );
        savedSources.push('MySQL');
      } catch (mysqlErr) {
        console.error(`MySQL save error for ${model}:`, mysqlErr.message);
      }
    }

    if (savedSources.length === 0) {
      return res.status(503).json({ error: 'Could not save to any database' });
    }

    res.status(201).json({
      data: savedData,
      savedTo: savedSources,
      message: `Data saved to ${savedSources.join(' and ')}`
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ================================
// API ROUTES - UPDATE
// ================================

app.put('/api/:model/:id', async (req, res) => {
  const { model, id } = req.params;
  const updateData = req.body;
  const validModels = ['users', 'employees', 'tasks', 'projects', 'companies'];
  
  if (!validModels.includes(model)) {
    return res.status(400).json({ error: 'Invalid model' });
  }

  try {
    let updatedData = null;
    let updatedSources = [];

    // Update in MongoDB
    if (mongoConnected && mongoConnection) {
      try {
        updatedData = await mongoConnection[model].findByIdAndUpdate(
          id,
          updateData,
          { new: true }
        ).lean();
        if (updatedData) {
          updatedSources.push('MongoDB');
        }
      } catch (mongoErr) {
        console.error(`MongoDB update error for ${model}:`, mongoErr.message);
      }
    }

    // Update in MySQL
    if (mysqlConnected && mysqlPool) {
      try {
        const columns = Object.keys(updateData);
        const values = Object.values(updateData);
        const setClause = columns.map(col => `${col} = ?`).join(',');
        
        const [result] = await mysqlPool.query(
          `UPDATE ${model} SET ${setClause} WHERE id = ?`,
          [...values, id]
        );
        
        if (result.affectedRows > 0) {
          updatedSources.push('MySQL');
        }
      } catch (mysqlErr) {
        console.error(`MySQL update error for ${model}:`, mysqlErr.message);
      }
    }

    if (updatedSources.length === 0) {
      return res.status(404).json({ error: 'Record not found' });
    }

    res.json({
      data: updatedData || updateData,
      updatedIn: updatedSources,
      message: `Data updated in ${updatedSources.join(' and ')}`
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ================================
// API ROUTES - DELETE
// ================================

app.delete('/api/:model/:id', async (req, res) => {
  const { model, id } = req.params;
  const validModels = ['users', 'employees', 'tasks', 'projects', 'companies'];
  
  if (!validModels.includes(model)) {
    return res.status(400).json({ error: 'Invalid model' });
  }

  try {
    let deletedSources = [];

    // Delete from MongoDB
    if (mongoConnected && mongoConnection) {
      try {
        const result = await mongoConnection[model].findByIdAndDelete(id);
        if (result) {
          deletedSources.push('MongoDB');
        }
      } catch (mongoErr) {
        console.error(`MongoDB delete error for ${model}:`, mongoErr.message);
      }
    }

    // Delete from MySQL
    if (mysqlConnected && mysqlPool) {
      try {
        const [result] = await mysqlPool.query(
          `DELETE FROM ${model} WHERE id = ?`,
          [id]
        );
        
        if (result.affectedRows > 0) {
          deletedSources.push('MySQL');
        }
      } catch (mysqlErr) {
        console.error(`MySQL delete error for ${model}:`, mysqlErr.message);
      }
    }

    if (deletedSources.length === 0) {
      return res.status(404).json({ error: 'Record not found' });
    }

    res.json({
      success: true,
      deletedFrom: deletedSources,
      message: `Data deleted from ${deletedSources.join(' and ')}`
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ================================
// SPECIAL ROUTES - AUTHENTICATION
// ================================

app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password required' });
  }

  try {
    let user = null;
    let source = null;

    // Try MongoDB first
    if (mongoConnected && mongoConnection) {
      user = await mongoConnection.users.findOne({ email: email.toLowerCase() }).lean();
      if (user) source = 'MongoDB';
    }

    // Fallback to MySQL
    if (!user && mysqlConnected && mysqlPool) {
      const [rows] = await mysqlPool.query(
        'SELECT * FROM users WHERE email = ?',
        [email.toLowerCase()]
      );
      if (rows.length > 0) {
        user = rows[0];
        source = 'MySQL';
      }
    }

    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Password verification would go here
    // For now, just return user info
    res.json({
      success: true,
      user: {
        id: user.id || user._id,
        email: user.email,
        username: user.username,
        full_name: user.full_name,
        role: user.role
      },
      source
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ================================
// SERVER STATUS ENDPOINT
// ================================

app.get('/api/status', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    databases: {
      mongodb: {
        connected: mongoConnected,
        uri: MONGO_URI,
        database: 'taskvise'
      },
      mysql: {
        connected: mysqlConnected,
        host: MYSQL_CONFIG.host,
        database: MYSQL_CONFIG.database,
        port: MYSQL_CONFIG.port
      }
    },
    message: 'Server is running with dual database support'
  });
});

// ================================
// HEALTH CHECK ENDPOINT
// ================================

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    mongodb: mongoConnected ? '✅' : '❌',
    mysql: mysqlConnected ? '✅' : '❌'
  });
});

// ================================
// STATIC FILES & LANDING PAGE
// ================================

app.use(express.static(path.join(__dirname, 'static')));
app.use('/templates', express.static(path.join(__dirname, 'templates')));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'landing.html'));
});

app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'login.html'));
});

// ================================
// ERROR HANDLING
// ================================

app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// ================================
// START SERVER
// ================================

const PORT = process.env.PORT || 4000;

console.log('\n');
console.log('╔════════════════════════════════════════════════════════╗');
console.log('║        TASKVISE - NODE.JS SERVER INITIALIZING          ║');
console.log('╚════════════════════════════════════════════════════════╝');
console.log('');

app.listen(PORT, () => {
  console.log(`\n✨ Node.js Server Running on Port: ${PORT}`);
  console.log(`🌐 Local URL: http://localhost:${PORT}`);
  console.log('\n📊 Database Connections:');
  console.log(`   MongoDB: ${mongoConnected ? '✅ Connected' : '⏳ Connecting...'}${MONGO_URI}`);
  console.log(`   MySQL: ${mysqlConnected ? '✅ Connected' : '⏳ Connecting...'}${MYSQL_CONFIG.host}:${MYSQL_CONFIG.port}/${MYSQL_CONFIG.database}`);
  console.log('\n📍 Available Endpoints:');
  console.log('   GET  /api/status              - Server status');
  console.log('   GET  /health                  - Health check');
  console.log('   GET  /api/:model              - Get all records');
  console.log('   GET  /api/:model/:id          - Get by ID');
  console.log('   POST /api/:model              - Create record');
  console.log('   PUT  /api/:model/:id          - Update record');
  console.log('   DELETE /api/:model/:id        - Delete record');
  console.log('   POST /api/login               - User login');
  console.log('\n🔄 Data synchronizes automatically between MongoDB and MySQL');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
});

module.exports = app;
