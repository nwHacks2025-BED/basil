const express=require('express')
const cors = require('cors');
const { MongoClient } = require('mongodb');
const { spawn } = require('child_process');
const app = express();
app.use(cors());
const port=3000

let bestPosting = null;

let decisionsMade = 0;
let postingStack = [];

const uri = "mongodb+srv://davenfroberg:WjxywruYe42mXrVe@nwhacks.dtnoj.mongodb.net/?retryWrites=true&w=majority&appName=nwhacks"
const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });


// Initialize MongoDB connection - idea from chatGPT
async function connectDB() {
    if (!client) {
        client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });
        await client.connect();
    }
    return client;
}

async function getTopPostings(limit) {
    const client = await connectDB();
    try {
        const database = client.db('jobs');
        const collection = database.collection('unlabelled');
        const postings = await collection.find().sort({ jobId: -1 }).limit(limit).toArray();
        postingStack = postingStack.concat(postings);
        return postings;
    } catch (error) {
        console.error('Error in getTopPostings:', error);
        throw error;
    }
}

async function getShortlistedPostings() {
    const client = await connectDB();
    try {
        const database = client.db('jobs');
        const collection = database.collection('labelled');
        return await collection.find().toArray();
    } catch (error) {
        console.error('Error in getShortlistedPostings:', error);
        throw error;
    }
}

async function moveLabelledPosting(jobId, label) {
    const client = await connectDB();
    const session = client.startSession();

    try {
        await session.withTransaction(async () => {
            const database = client.db('jobs');
            
            // Find and store the document before deletion
            const doc = await database.collection('unlabelled').findOne({ job_id: jobId }, { session });
            if (!doc) {
                throw new Error('Document not found in unlabelled collection');
            }

            // Delete from unlabelled collection
            const deleteResult = await database.collection('unlabelled')
                .deleteOne({ job_id: jobId }, { session });
            if (deleteResult.deletedCount !== 1) {
                throw new Error('Failed to delete document from unlabelled collection');
            }

            // Remove probability field and add new fields
            const { probability, ...docWithoutProbability } = doc;
            const enrichedDoc = {
                ...docWithoutProbability,
                apply: label
            };

            // Insert into labelled collection
            const insertResult = await database.collection('labelled')
                .insertOne(enrichedDoc, { session });
            if (!insertResult.acknowledged) {
                throw new Error('Failed to insert document into labelled collection');
            }

            return enrichedDoc;
        });
    } catch (error) {
        console.error('Error in moveLabelledPosting:', error);
        throw error;
    } finally {
        await session.endSession();
    }
}

function runPythonPreprocessing() {
    return new Promise((resolve, reject) => {
        // Assuming Python 3 is installed and in your PATH
        const pythonProcess = spawn('python3', ['preprocessing.py']);

        // Handle data from the Python script
        pythonProcess.stdout.on('data', (data) => {
            console.log('Python output:', data.toString());
        });

        // Handle errors
        pythonProcess.stderr.on('data', (data) => {
            console.error('Python error:', data.toString());
        });

        // Handle process completion
        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                reject(`Python process exited with code ${code}`);
            } else {
                resolve('Python script completed successfully');
            }
        });
    });
}

app.get('/best-posting', async (req, res) => {
    try {
        if (!bestPosting) {
            if (postingStack.length <= 1) {
                await getTopPostings(10);
            }
            if (postingStack.length === 0) {
                return res.status(404).send("No more postings available.");
            }
            bestPosting = postingStack.pop();
            decisionsMade++;
        }
        if (decisionsMade % 5 === 0) {
            console.log('Training the model...');
            // TODO print something to the UI to indicate that the model is being trained
            runPythonPreprocessing();
        }
        const response = { remainingLocally: postingStack.length, ...bestPosting };
        res.json(response);
    } catch (error) {
        console.error('Error in /best-posting:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.post('/skip', async (req, res) => {
    try {
        if (!postingStack.length) {
            bestPosting = null;
            return res.status(404).send("No more postings available.");
        }

        const currentPosting = bestPosting;
        bestPosting = postingStack.pop();
        decisionsMade++;

        console.log("Current posting job_id:", currentPosting.job_id); // Debug line
        const result = await moveLabelledPosting(currentPosting.job_id, 0);
        res.status(201).json({ message: "Posting skipped", result });
    } catch (error) {
        console.error('Error in /skip:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
    
});

app.post('/shortlist', async (req, res) => {
    try {
        if (!postingStack.length) {
            bestPosting = null;
            return res.status(404).send("No more postings available.");
        }

        const currentPosting = bestPosting;
        bestPosting = postingStack.pop();
        decisionsMade++;
        
        const result = await moveLabelledPosting(currentPosting.job_id, 1);
        try {
            const shortlist = await getShortlistedPostings();
            if (!shortlist || shortlist.length === 0) {
                return res.status(404).send("No shortlisted postings available.");
            }
            res.status(200).json(shortlist);
        } catch (error) {
            console.error('Error in /shortlist:', error);
            res.status(500).json({ error: 'Internal server error' });
        }
    } catch (error) {
        console.error('Error in /shortlist:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
    
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});

// Graceful shutdown - idea from chatGPT
process.on('SIGINT', async () => {
    try {
        if (client) {
            await client.close();
            console.log('MongoDB connection closed.');
        }
        process.exit(0);
    } catch (error) {
        console.error('Error during shutdown:', error);
        process.exit(1);
    }
});