import { initializeApp } from 'firebase/app';
import { getDatabase } from 'firebase/database';

let database = null;

const initializeFirebase = () => {
  if (!database) {
    const firebaseConfig = {
      databaseURL: process.env.REACT_APP_FIREBASE_URL
    };
    const app = initializeApp(firebaseConfig);
    database = getDatabase(app);
  }
  return database;
};

export const getFirebaseDatabase = () => {
  return initializeFirebase();
}; 