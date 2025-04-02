import { config } from 'dotenv';
import { resolve } from 'path';
import { initializeApp } from 'firebase/app';
import { getDatabase, ref, onValue, DataSnapshot } from 'firebase/database';
import { getFirestore, doc, setDoc } from 'firebase/firestore';

// Load environment variables from .env file
config({ path: resolve(__dirname, '../../.env') });

// Initialize Firebase
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID,
  databaseURL: process.env.REACT_APP_FIREBASE_DATABASE_URL
};

console.log('Firebase config:', firebaseConfig);

const app = initializeApp(firebaseConfig);
const database = getDatabase(app);
const db = getFirestore(app);

console.log('Starting migration from Realtime Database to Firestore...');

// Reference to the phoneLeads node in Realtime Database
const phoneLeadsRef = ref(database, 'phoneLeads');

// Listen for data from Realtime Database
onValue(phoneLeadsRef, async (snapshot: DataSnapshot) => {
  try {
    const data = snapshot.val();
    if (!data) {
      console.log('No data found in Realtime Database');
      return;
    }

    console.log('Received data from Realtime Database');
    console.log('Number of cities:', Object.keys(data).length);

    // Process each city
    for (const city of Object.keys(data)) {
      console.log(`Processing city: ${city}`);
      const cityData = data[city];

      // Process each business type in the city
      for (const businessType of Object.keys(cityData)) {
        console.log(`Processing business type: ${businessType}`);
        const businessData = cityData[businessType];

        // Create a document reference in Firestore
        const docRef = doc(db, 'phoneLeads', `${city}_${businessType}`);

        // Prepare the data for Firestore
        const firestoreData = {
          city,
          businessType,
          leads: businessData,
          lastUpdated: new Date().toISOString()
        };

        // Save to Firestore
        await setDoc(docRef, firestoreData);
        console.log(`Successfully migrated data for ${city} - ${businessType}`);
      }
    }

    console.log('Migration completed successfully!');
  } catch (error: unknown) {
    console.error('Error during migration:', error);
  }
}, (error: Error) => {
  console.error('Error reading from Realtime Database:', error);
});

// Keep the script running
process.on('SIGINT', () => {
  console.log('Migration script terminated by user');
  process.exit(0);
});

export {}; 