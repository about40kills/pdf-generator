const createError = require('http-errors');
const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const bodyParser = require('body-parser');
const session = require('express-session');
const os = require('os');

const indexRouter = require('./routes/index');
const usersRouter = require('./routes/users');
const cvRouter = require('./routes/cv');

const app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

app.use(logger('dev'));
app.use(session({secret: '12345678', resave: false, saveUninitialized: true}));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// Serve files from temporary directory
const tempDir = path.join(os.tmpdir(), 'pdf-generator');
app.use('/images', express.static(path.join(tempDir, 'images')));
app.use('/pdf', express.static(path.join(tempDir, 'pdfs')));

app.use(bodyParser.json());

app.use('/', indexRouter);
app.use('/users', usersRouter);
app.use('/cv', cvRouter);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.locals.title = 'Error Page';
  res.render('error');
});

module.exports = app;
