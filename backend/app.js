const express=require('express')
const cors = require('cors');
const { MongoClient } = require('mongodb');
const app = express();
app.use(cors());
const port=3000

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});

let bestPosting = null;

let postingStack = [];

app.post('/skip', (req, res) => {
    if (postingStack) {
        bestPosting = postingStack.pop();
        // remove the posting from unlabelled and add it to labelled (MONGODB)
        res.send("done!")
    } else {
        bestPosting = null;
        res.status(500).send("No more postings available.");
        return;
    }
    
});

const uri = "mongodb+srv://davenfroberg:WjxywruYe42mXrVe@nwhacks.dtnoj.mongodb.net/?retryWrites=true&w=majority&appName=nwhacks"
const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });

async function getTopPostings(limit) {
    try {
        await client.connect();
        const database = client.db('jobs');
        const collection = database.collection('unlabelled');
        const postings = await collection.find().sort({ jobId: -1 }).limit(limit).toArray();
        postingStack = postingStack.concat(postings);
    } catch (error) {
        console.error(error);
    } finally {
        await client.close();
    }
}

app.get('/best-posting', (req, res) => {
    if (!bestPosting) {
        if (postingStack.length === 0) {
            getTopPostings(10);
        }
        if (postingStack.length === 0) {
            res.status(500).send("No more postings available.");
            return;
        }
        bestPosting = postingStack.pop();
    }
    const response = {remainingLocally: postingStack.length, ...bestPosting};
    res.json(response);
});


