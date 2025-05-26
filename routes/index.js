const express = require('express');
const router = express.Router();
const path = require('path');
const multer = require('multer');
const fs = require('fs');
const PDFDocument = require('pdfkit');
const bodyParser = require('body-parser');
const os = require('os');

// Create temporary directories outside the app directory
const tempDir = path.join(os.tmpdir(), 'pdf-generator');
const imageDir = path.join(tempDir, 'images');
const pdfDir = path.join(tempDir, 'pdfs');

// Ensure temporary directories exist
if (!fs.existsSync(tempDir)) {
  fs.mkdirSync(tempDir, { recursive: true });
}
if (!fs.existsSync(imageDir)) {
  fs.mkdirSync(imageDir, { recursive: true });
}
if (!fs.existsSync(pdfDir)) {
  fs.mkdirSync(pdfDir, { recursive: true });
}

// Set up multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, imageDir);
  },
  filename: (req, file, cb) => {
    cb(null, file.fieldname + '-' + Date.now() + '.' + file.mimetype.split('/')[1]);
  }
});

//config for file filtering
const fileFilter = (req, file, cb) => {
  // accept images only
  const ext = path.extname(file.originalname);
  if (ext !== '.jpg' && ext !== '.jpeg' && ext !== '.png') {
    return cb(new Error('Only .jpg, .jpeg and .png format allowed!'));
  } else {
    return cb(null, true)
  }
}

//initialize multer with the storage and fileFilter options
const upload = multer({ storage, fileFilter: fileFilter });

//upload section for the images
router.post('/upload', upload.array('images'), (req, res) => {
    try {
      console.log('Files received:', req.files);
      const files = req.files; 
      const imgNames = files.map(file => file.filename);  
      req.session.imagefiles = imgNames;
      res.redirect('/'); 
    } catch (err) {
      console.error('Error in /upload:', err);
      res.status(500).send('Upload failed');
    }
});

router.post('/new', upload.array('images'), (req, res) => {
  console.log('Additional files received:', req.files);
  const files = req.files;
  const imgNames = [];

  // Loop through the files and get the names
  for(const file of files){
    imgNames.push(file.filename);  
  }

  //add additional image names to the session or create new session if none exists
  if (req.session.imagefiles){
    req.session.imagefiles = [...req.session.imagefiles, ...imgNames];
  } else {
    req.session.imagefiles = imgNames;
  }

  // send the names back to the client
  res.redirect('/');
});

router.post('/pdf', (req, res, next) => {
  let body = req.body;

  //create a new pdf document
  let doc = new PDFDocument({size: 'A4', autoFirstPage: false});
  let pdfName = 'pdf-' + Date.now() + '.pdf'; 

  //store the pdf in the temporary directory
  doc.pipe(fs.createWriteStream(path.join(pdfDir, pdfName)));
 
  // Add each image to a new page
  for(let name of body){
    doc.addPage();
    try {
      doc.image(path.join(imageDir, name), 20, 20, {
        width: 555.28, 
        align: 'center', 
        valign: 'center'
      });
    } catch (err) {
      console.error(`Error adding image ${name} to PDF:`, err);
    }
  }
 
  // Handle PDF completion
  doc.on('end', () => {
    console.log('PDF created successfully:', pdfName);
  });

  // Finalize the PDF
  doc.end();
  
  // Send the PDF URL to the client after the PDF is created
  res.send(`/pdf/${pdfName}`);
});

router.get('/reset', (req, res) => {
  //delete data from the session
  req.session.imagefiles = undefined;

  //redirect to the index page
  res.redirect('/');
});

/* user sends a GET request to the root URL */
// and the server responds with the index.html file
router.get('/', (req, res, next)  => {
  //if there are no image filenames in a session, return to the html page
  if (req.session.imagefiles === undefined) {
    res.sendFile(path.join(__dirname, '..', 'public/html/index.html'));
  } else {
    //if there are image filenames in a session, return the index.jade(images)
    res.render('index', {images: req.session.imagefiles});
  }
});

module.exports = router;
