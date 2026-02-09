import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/Sidebar';

export const metadata: Metadata = {
    title: 'Actas PG - Gestión de Equipos Electromédicos',
    description: 'Sistema de gestión de actas de recepción y baja de equipos electromédicos',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="es">
            <body>
                <div className="app-container">
                    <Sidebar />
                    <main className="main-content">
                        {children}
                    </main>
                </div>
            </body>
        </html>
    );
}
