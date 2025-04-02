import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "AIzaSyC6NFGd0CAAjRFpmwbFtqcbSPtPnXn-1Qs",
  authDomain: "emailsender-44bcc.firebaseapp.com",
  databaseURL: "https://emailsender-44bcc-default-rtdb.firebaseio.com",
  projectId: "emailsender-44bcc",
  storageBucket: "emailsender-44bcc.firebasestorage.app",
  messagingSenderId: "822067962378",
  appId: "1:822067962378:web:a140218cdea9c5bbcbf5f3",
  measurementId: "G-19YF4KZX7S"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firestore
const db = getFirestore(app);

export { db }; 