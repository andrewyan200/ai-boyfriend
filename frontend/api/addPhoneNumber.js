const { GoogleSpreadsheet } = require("google-spreadsheet");
const { JWT } = require("google-auth-library");

const serviceAccountAuth = new JWT({
  email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
  key: process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/gm, "\n"), // Ensure that newlines are correctly formatted
  scopes: ["https://www.googleapis.com/auth/spreadsheets"],
});

const doc = new GoogleSpreadsheet(
  "1AQNxaU1pOnEQq-LKRgW2Kj7j_lCjvOKcR9l6rPJm4d4",
  serviceAccountAuth
);

async function authenticateGoogleSheets() {
  await doc.loadInfo(); // loads document properties and worksheets
}

// Serverless function to add phone number
module.exports = async (req, res) => {
  if (req.method === "POST") {
    try {
      await authenticateGoogleSheets();

      const sheet = doc.sheetsByIndex[0];

      // Generate a timestamp
      const timestamp = new Date().toISOString();

      // Add a row with both the phone number and timestamp
      await sheet.addRow({ PhoneNumber: req.body.phoneNumber, Timestamp: timestamp });

      res.status(200).send("Phone number and timestamp added");
    } catch (error) {
      console.error("Error:", error);
      res.status(500).send("Error adding phone number and timestamp");
    }
  } else {
    res.status(405).send("Method not allowed");
  }
};
