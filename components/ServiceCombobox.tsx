'use client';

import { useState, useEffect, useRef } from 'react';
import { ChevronDown } from 'lucide-react';

interface Service {
    manager?: string;
    unit?: string;
    floor?: string;
    hole?: string;
    center_name?: string;
    center_code?: string;
}

interface ServiceComboboxProps {
    services: Record<string, Service>;
    value: string;
    onChange: (value: string, serviceData?: Service) => void;
    label?: string;
}

export default function ServiceCombobox({
    services,
    value,
    onChange,
    label = 'Servicio (Buscador)'
}: ServiceComboboxProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [search, setSearch] = useState(value);
    const wrapperRef = useRef<HTMLDivElement>(null);

    const serviceList = Object.keys(services).sort();
    const filtered = serviceList.filter(s =>
        s.toLowerCase().includes(search.toLowerCase())
    );

    useEffect(() => {
        setSearch(value);
    }, [value]);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleSelect = (serviceName: string) => {
        if (serviceName === '➕ AÑADIR NUEVO...') {
            onChange('');
            setSearch('');
        } else {
            onChange(serviceName, services[serviceName]);
            setSearch(serviceName);
        }
        setIsOpen(false);
    };

    return (
        <div className="form-group" ref={wrapperRef}>
            <label className="form-label">{label}</label>
            <div style={{ position: 'relative' }}>
                <input
                    type="text"
                    className="form-input"
                    value={search}
                    onChange={(e) => {
                        setSearch(e.target.value);
                        setIsOpen(true);
                    }}
                    onFocus={() => setIsOpen(true)}
                    placeholder="Buscar o añadir servicio..."
                    style={{ paddingRight: '2.5rem' }}
                />
                <ChevronDown
                    style={{
                        position: 'absolute',
                        right: '1rem',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        color: 'var(--q-text-muted)',
                        pointerEvents: 'none'
                    }}
                    size={18}
                />

                {isOpen && (
                    <div style={{
                        position: 'absolute',
                        top: '100%',
                        left: 0,
                        right: 0,
                        background: 'var(--q-card)',
                        border: '1px solid var(--q-border)',
                        borderRadius: '12px',
                        marginTop: '4px',
                        maxHeight: '200px',
                        overflowY: 'auto',
                        zIndex: 50,
                        boxShadow: 'var(--q-shadow-premium)'
                    }}>
                        {filtered.length > 0 ? (
                            filtered.map(service => (
                                <div
                                    key={service}
                                    onClick={() => handleSelect(service)}
                                    style={{
                                        padding: '0.75rem 1rem',
                                        cursor: 'pointer',
                                        borderBottom: '1px solid var(--q-border)',
                                        transition: 'background 0.2s'
                                    }}
                                    onMouseEnter={(e) => e.currentTarget.style.background = 'var(--q-bg)'}
                                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                >
                                    {service}
                                </div>
                            ))
                        ) : search && (
                            <div
                                onClick={() => handleSelect('➕ AÑADIR NUEVO...')}
                                style={{
                                    padding: '0.75rem 1rem',
                                    cursor: 'pointer',
                                    color: 'var(--q-primary)',
                                    fontWeight: 600
                                }}
                            >
                                ➕ Añadir "{search}" como nuevo servicio
                            </div>
                        )}
                        <div
                            onClick={() => handleSelect('➕ AÑADIR NUEVO...')}
                            style={{
                                padding: '0.75rem 1rem',
                                cursor: 'pointer',
                                color: 'var(--q-primary)',
                                fontWeight: 600,
                                borderTop: '1px solid var(--q-border)'
                            }}
                        >
                            ➕ AÑADIR NUEVO...
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
