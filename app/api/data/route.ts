import { NextRequest, NextResponse } from 'next/server';
import { getFirebaseAdmin, COLLECTION, DOCUMENT } from '@/lib/firebase';

export async function GET() {
    try {
        const firebase = getFirebaseAdmin();

        if (!firebase) {
            // Return default data if Firebase is not configured
            return NextResponse.json({
                defaults: {
                    services: {},
                    models: {}
                }
            });
        }

        const { db } = firebase;
        const docRef = db.collection(COLLECTION).doc(DOCUMENT);
        const doc = await docRef.get();

        if (doc.exists) {
            return NextResponse.json(doc.data());
        }

        return NextResponse.json({
            defaults: {
                services: {},
                models: {}
            }
        });
    } catch (error) {
        console.error('Error fetching data:', error);
        return NextResponse.json(
            { error: 'Failed to fetch data' },
            { status: 500 }
        );
    }
}

export async function POST(request: NextRequest) {
    try {
        const firebase = getFirebaseAdmin();
        const body = await request.json();

        if (!firebase) {
            // In local mode, just return success
            return NextResponse.json({ success: true, mode: 'local' });
        }

        const { db } = firebase;
        const docRef = db.collection(COLLECTION).doc(DOCUMENT);
        await docRef.set(body);

        return NextResponse.json({ success: true, mode: 'cloud' });
    } catch (error) {
        console.error('Error saving data:', error);
        return NextResponse.json(
            { error: 'Failed to save data' },
            { status: 500 }
        );
    }
}
