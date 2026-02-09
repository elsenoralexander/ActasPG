'use client';

import { useState, useEffect, useRef } from 'react';
import { ChevronDown } from 'lucide-react';

interface Model {
    description?: string;
    brand?: string;
    provider?: string;
    contact?: string;
}

interface ModelComboboxProps {
    models: Record<string, Model>;
    value: string;
    onChange: (value: string, modelData?: Model) => void;
    label?: string;
}

export default function ModelCombobox({
    models,
    value,
    onChange,
    label = 'Modelo (Buscador)'
}: ModelComboboxProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [search, setSearch] = useState(value);
    const wrapperRef = useRef<HTMLDivElement>(null);

    const modelList = Object.keys(models).sort();
    const filtered = modelList.filter(m =>
        m.toLowerCase().includes(search.toLowerCase())
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

    const handleSelect = (modelName: string) => {
        if (modelName === '➕ AÑADIR NUEVO...') {
            onChange('');
            setSearch('');
        } else {
            onChange(modelName, models[modelName]);
            setSearch(modelName);
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
                    placeholder="Buscar o añadir modelo..."
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
                            filtered.map(model => (
                                <div
                                    key={model}
                                    onClick={() => handleSelect(model)}
                                    style={{
                                        padding: '0.75rem 1rem',
                                        cursor: 'pointer',
                                        borderBottom: '1px solid var(--q-border)',
                                        transition: 'background 0.2s'
                                    }}
                                    onMouseEnter={(e) => e.currentTarget.style.background = 'var(--q-bg)'}
                                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                >
                                    <div style={{ fontWeight: 500 }}>{model}</div>
                                    {models[model]?.description && (
                                        <div style={{ fontSize: '0.8rem', color: 'var(--q-text-muted)' }}>
                                            {models[model].description}
                                        </div>
                                    )}
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
                                ➕ Añadir "{search}" como nuevo modelo
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
