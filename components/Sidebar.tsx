'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ClipboardList, Trash2, Database } from 'lucide-react';

const navItems = [
    { href: '/recepcion', label: '📋 Recepción', icon: ClipboardList },
    { href: '/baja', label: '🗑️ Baja', icon: Trash2 },
    { href: '/database', label: '💾 Base de Datos', icon: Database },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="sidebar">
            <div style={{ padding: '1rem 0 1.5rem 0' }}>
                <h2 style={{
                    margin: 0,
                    fontSize: '1.6rem',
                    color: '#023E54',
                    fontFamily: '"Outfit", sans-serif',
                    fontWeight: 800
                }}>
                    ACTAS PG
                </h2>
                <div className="status-badge cloud" style={{ marginTop: '8px' }}>
                    <span className="status-dot"></span>
                    Cloud Sync Activo
                </div>
            </div>

            <p style={{
                fontSize: '0.7rem',
                fontWeight: 700,
                color: 'var(--q-text-muted)',
                margin: '1rem 0 0.5rem 0',
                textTransform: 'uppercase',
                letterSpacing: '0.1em'
            }}>
                Sección
            </p>

            <nav>
                {navItems.map((item) => (
                    <Link
                        key={item.href}
                        href={item.href}
                        className={`nav-item ${pathname === item.href ? 'active' : ''}`}
                    >
                        {item.label}
                    </Link>
                ))}
            </nav>

            <div style={{
                marginTop: 'auto',
                color: '#94A3B8',
                fontSize: '0.7rem',
                fontWeight: 500
            }}>
                v4.0 • Next.js + Vercel
            </div>
        </aside>
    );
}
