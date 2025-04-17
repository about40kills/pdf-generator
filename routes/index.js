const express = require('express');
const router = express.Router();
const path = require('path');
const multer = require('multer');
const fs = require('fs');
const PDFDocument = require('pdfkit');
const bodyParser = require('body-parser');

// Ensure directories exist
const imageDir = path.join(__dirname, '..', 'public/images');
if (!fs.existsSync(imageDir)) {
  fs.mkdirSync(imageDir, { recursive: true });
}

const pdfDir = path.join(__dirname, '..', 'public/pdf');
if (!fs.existsSync(pdfDir)) {
  fs.mkdirSync(pdfDir, { recursive: true });
}


// Set up multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const destPath = path.join(__dirname, '..', 'public/images');
    if (!fs.existsSync(destPath)) {
      fs.mkdirSync(destPath, { recursive: true });
      console.log('Created images directory');
    }
    cb(null, destPath);
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



//upload seection for the images
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
}) 

router.post('/pdf', (req, res, next) => {
  let body = req.body;

  //create a new pdf document
  let doc = new PDFDocument({size: 'A4', autoFirstPage: false});
  let pdfName = 'pdf-' + Date.now() + '.pdf'; 


  //store the pdf in the public/pdf directory
  doc.pipe(fs.createWriteStream(path.join(__dirname, '..', `public/pdf/${pdfName}`)));
 
 // Add each image to a new page
 for(let name of body){
  doc.addPage();
  try {
    doc.image(path.join(__dirname, '..', 'public/images', name), 20, 20, {
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
})


router.get('/reset', (req, res) => {
  //delete the files stored in session
  let files = req.session.imagefiles;

  if (files && files.length > 0) {
    let deleteFiles = async(paths) => {
      try {
        const { unlink } = require('fs').promises;
        let deleting = paths.map((file) => 
          unlink(path.join(__dirname, '..', 'public/images', file))
            .catch(err => {
              console.error(`Failed to delete file ${file}:`, err);
            })
        );
        await Promise.all(deleting);
        console.log('All files deleted successfully');
      } catch (error) {
        console.error('Error during file deletion:', error);
      }
    }
    
    deleteFiles(files)
      .catch(err => console.error('Error in deleteFiles:', err));
  } else {
    console.log('No files to delete');
  }

  //delete the files stored in the public/images directory
  const imagesDir = path.join(__dirname, '..', 'public/images');
  fs.readdir(imagesDir, (err, allFiles) => {
    if (err) {
      console.error('Error reading images directory:', err);
    } else {
      // Filter files to delete only image files
      const imagesToDelete = allFiles.filter(file => {
        // Keep any special files you need (like .gitkeep)
        if (file === '.gitkeep' || file === '.DS_Store') {
          return false;
        }
        // Keep only image files (optional filter if you have other files there)
        const ext = path.extname(file).toLowerCase();
        return ext === '.jpg' || ext === '.jpeg' || ext === '.png';
      });
      
      // Delete each file
      if (imagesToDelete.length > 0) {
        const { unlink } = require('fs').promises;
        imagesToDelete.forEach(file => {
          unlink(path.join(imagesDir, file))
            .catch(err => console.error(`Failed to delete ${file}:`, err));
        });
        console.log(`Deleted ${imagesToDelete.length} image files from folder`);
      } else {
        console.log('No images found in folder to delete');
      }
    }
  });


  //delete the files stored in the public/pdf directory
  const pdfDir = path.join(__dirname, '..', 'public/pdf');
  fs.readdir(pdfDir, (err, allFiles) => {
    if (err) {
      console.error('Error reading PDF directory:', err);
    } else {
      // Filter files to delete only PDF files
      const pdfsToDelete = allFiles.filter(file => {
        // Keep any special files you need (like .gitkeep)
        if (file === '.gitkeep' || file === '.DS_Store') {
          return false;
        }
        // Keep only PDF files
        const ext = path.extname(file).toLowerCase();
        return ext === '.pdf';
      });
      
      // Delete each file
      if (pdfsToDelete.length > 0) {
        const { unlink } = require('fs').promises;
        pdfsToDelete.forEach(file => {
          unlink(path.join(pdfDir, file))
            .catch(err => console.error(`Failed to delete PDF ${file}:`, err));
        });
        console.log(`Deleted ${pdfsToDelete.length} PDF files from folder`);
      } else {
        console.log('No PDFs found in folder to delete');
      }
    }
  });

  //delete data from the session
  req.session.imagefiles = undefined;

  //redirect to the index page
  res.redirect('/');

})
 
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
