import { initializeApp, getApps, cert, App } from 'firebase-admin/app';
import { getFirestore, Firestore } from 'firebase-admin/firestore';

let app: App | undefined;
let db: Firestore | undefined;

export function getFirebaseAdmin(): { app: App; db: Firestore } | null {
    if (!process.env.FIREBASE_SERVICE_ACCOUNT) {
        console.warn('FIREBASE_SERVICE_ACCOUNT not set - running in local mode');
        return null;
    }

    if (!app) {
        try {
            const serviceAccount = JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT);

            if (getApps().length === 0) {
                app = initializeApp({
                    credential: cert(serviceAccount),
                });
            } else {
                app = getApps()[0];
            }

            db = getFirestore(app);
        } catch (error) {
            console.error('Failed to initialize Firebase:', error);
            return null;
        }
    }

    return { app: app!, db: db! };
}

export const COLLECTION = 'app_data';
export const DOCUMENT = 'memory';
