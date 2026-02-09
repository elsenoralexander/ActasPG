'use client';

import { useState, useEffect } from 'react';
import ServiceCombobox from '@/components/ServiceCombobox';
import ModelCombobox from '@/components/ModelCombobox';

interface Component {
    name: string;
    inventory: string;
    brand: string;
    model: string;
    serial: string;
}

interface FormData {
    center_name: string;
    center_code: string;
    service: string;
    manager: string;
    unit: string;
    floor: string;
    hole: string;
    description: string;
    brand: string;
    model: string;
    serial_number: string;
    provider: string;
    property: string;
    contact: string;
    reception_date: string;
    acceptance_date: string;
    warranty_end: string;
    warranty_years: number;
    periodicity: string;
    main_inventory_number: string;
    parent_inventory_number: string;
    order_number: string;
    amount_tax_included: string;
    compliance: boolean;
    manuals_usage: boolean;
    manuals_tech: boolean;
    order_accordance: boolean;
    patient_data: boolean;
    backup_required: boolean;
    requires_epis: boolean;
    safe_to_use: boolean;
    received_correctly: boolean;
    users_trained: boolean;
    preventive_maintenance: boolean;
    maintenance_contract: boolean;
    equipment_status: string;
    observations: string;
    components: Component[];
}

const DEFAULT_FORM: FormData = {
    center_name: 'POLICLINICA GIPUZKOA',
    center_code: 'T05-POLGIP-HOS',
    service: '',
    manager: '',
    unit: '',
    floor: '',
    hole: '',
    description: '',
    brand: '',
    model: '',
    serial_number: '',
    provider: '',
    property: '',
    contact: '',
    reception_date: new Date().toISOString().split('T')[0],
    acceptance_date: new Date().toISOString().split('T')[0],
    warranty_end: '',
    warranty_years: 2,
    periodicity: 'Anual',
    main_inventory_number: 'INV-',
    parent_inventory_number: '',
    order_number: '',
    amount_tax_included: '',
    compliance: true,
    manuals_usage: true,
    manuals_tech: true,
    order_accordance: true,
    patient_data: true,
    backup_required: true,
    requires_epis: true,
    safe_to_use: true,
    received_correctly: true,
    users_trained: true,
    preventive_maintenance: true,
    maintenance_contract: true,
    equipment_status: 'good',
    observations: '',
    components: [],
};

export default function RecepcionPage() {
    const [form, setForm] = useState<FormData>(DEFAULT_FORM);
    const [memory, setMemory] = useState<any>({ defaults: { services: {}, models: {} } });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
    const [activeTab, setActiveTab] = useState<'general' | 'seguridad' | 'mantenimiento'>('general');

    useEffect(() => {
        fetch('/api/data')
            .then(res => res.json())
            .then(data => setMemory(data))
            .catch(console.error);
    }, []);

    useEffect(() => {
        // Calculate warranty end when acceptance date or years change
        if (form.acceptance_date && form.warranty_years > 0) {
            const date = new Date(form.acceptance_date);
            date.setFullYear(date.getFullYear() + form.warranty_years);
            setForm(f => ({ ...f, warranty_end: date.toISOString().split('T')[0] }));
        }
    }, [form.acceptance_date, form.warranty_years]);

    const handleServiceSelect = (serviceName: string, serviceData?: any) => {
        if (serviceData) {
            setForm(f => ({
                ...f,
                service: serviceName,
                manager: serviceData.manager || f.manager,
                floor: serviceData.floor || f.floor,
                unit: serviceData.unit || f.unit,
                hole: serviceData.hole || f.hole,
                center_name: serviceData.center_name || f.center_name,
                center_code: serviceData.center_code || f.center_code,
            }));
        } else {
            setForm(f => ({ ...f, service: serviceName }));
        }
    };

    const handleModelSelect = (modelName: string, modelData?: any) => {
        if (modelData) {
            setForm(f => ({
                ...f,
                model: modelName,
                description: modelData.description || f.description,
                brand: modelData.brand || f.brand,
                provider: modelData.provider || f.provider,
                contact: modelData.contact || f.contact,
            }));
        } else {
            setForm(f => ({ ...f, model: modelName }));
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        if (type === 'checkbox') {
            setForm(f => ({ ...f, [name]: (e.target as HTMLInputElement).checked }));
        } else {
            setForm(f => ({ ...f, [name]: value }));
        }
    };

    const handleComponentChange = (index: number, field: keyof Component, value: string) => {
        const updated = [...form.components];
        updated[index] = { ...updated[index], [field]: value };
        setForm(f => ({ ...f, components: updated }));
    };

    const addComponent = (withBrand = false) => {
        setForm(f => ({
            ...f,
            components: [...f.components, { name: '', inventory: '', brand: withBrand ? f.brand : '', model: '', serial: '' }]
        }));
    };

    const removeComponent = (index: number) => {
        setForm(f => ({
            ...f,
            components: f.components.filter((_, i) => i !== index)
        }));
    };

    const handleClear = () => {
        setForm(DEFAULT_FORM);
        setMessage(null);
    };

    const handleSubmit = async () => {
        setLoading(true);
        setMessage(null);

        try {
            // Save to memory
            const updatedMemory = { ...memory };
            if (form.service) {
                updatedMemory.defaults.services[form.service] = {
                    manager: form.manager,
                    unit: form.unit,
                    floor: form.floor,
                    hole: form.hole,
                    center_name: form.center_name,
                    center_code: form.center_code,
                };
            }
            if (form.model) {
                updatedMemory.defaults.models[form.model] = {
                    description: form.description,
                    brand: form.brand,
                    provider: form.provider,
                    contact: form.contact,
                };
            }
            await fetch('/api/data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedMemory),
            });
            setMemory(updatedMemory);

            // Generate PDF
            const response = await fetch('/api/pdf/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    data: {
                        ...form,
                        reception_date: formatDate(form.reception_date),
                        acceptance_date: formatDate(form.acceptance_date),
                        warranty_end: formatDate(form.warranty_end),
                    },
                    reportType: 'recepcion',
                }),
            });

            if (!response.ok) throw new Error('Error generating PDF');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Acta_Recepcion_${form.serial_number || 'EQUIPO'}.pdf`;
            a.click();
            window.URL.revokeObjectURL(url);

            setMessage({ type: 'success', text: '✅ Acta de Recepción generada con éxito.' });
        } catch (error) {
            console.error(error);
            setMessage({ type: 'error', text: '❌ Error generando el PDF.' });
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateStr: string) => {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleDateString('es-ES');
    };

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h1>📋 Nueva Acta de Recepción</h1>
                <button className="btn btn-secondary" onClick={handleClear}>
                    🧹 Limpiar Formulario
                </button>
            </div>

            {message && (
                <div className={`alert alert-${message.type === 'success' ? 'success' : 'error'}`}>
                    {message.text}
                </div>
            )}

            <div className="grid-2">
                {/* Column 1 */}
                <div>
                    <ServiceCombobox
                        services={memory.defaults.services}
                        value={form.service}
                        onChange={handleServiceSelect}
                    />

                    <div className="form-group">
                        <label className="form-label">Servicio</label>
                        <input type="text" className="form-input" name="service" value={form.service} onChange={handleChange} />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Centro</label>
                        <input type="text" className="form-input" name="center_name" value={form.center_name} onChange={handleChange} />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Código Centro</label>
                        <input type="text" className="form-input" name="center_code" value={form.center_code} onChange={handleChange} />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Responsable</label>
                        <input type="text" className="form-input" name="manager" value={form.manager} onChange={handleChange} />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Unidad</label>
                        <input type="text" className="form-input" name="unit" value={form.unit} onChange={handleChange} />
                    </div>

                    <div className="grid-2">
                        <div className="form-group">
                            <label className="form-label">Planta</label>
                            <input type="text" className="form-input" name="floor" value={form.floor} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Hueco</label>
                            <input type="text" className="form-input" name="hole" value={form.hole} onChange={handleChange} />
                        </div>
                    </div>
                </div>

                {/* Column 2 */}
                <div>
                    <div className="form-group">
                        <label className="form-label">Descripción</label>
                        <input type="text" className="form-input" name="description" value={form.description} onChange={handleChange} />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Marca</label>
                        <input type="text" className="form-input" name="brand" value={form.brand} onChange={handleChange} />
                    </div>

                    <ModelCombobox
                        models={memory.defaults.models}
                        value={form.model}
                        onChange={handleModelSelect}
                    />

                    <div className="form-group">
                        <label className="form-label">Modelo</label>
                        <input type="text" className="form-input" name="model" value={form.model} onChange={handleChange} />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Nº Serie</label>
                        <input type="text" className="form-input" name="serial_number" value={form.serial_number} onChange={handleChange} />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Proveedor</label>
                        <input type="text" className="form-input" name="provider" value={form.provider} onChange={handleChange} />
                    </div>

                    <div className="grid-2">
                        <div className="form-group">
                            <label className="form-label">Propiedad</label>
                            <input type="text" className="form-input" name="property" value={form.property} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Contacto</label>
                            <input type="text" className="form-input" name="contact" value={form.contact} onChange={handleChange} />
                        </div>
                    </div>

                    {/* Dates Card */}
                    <div className="card" style={{ marginTop: '1rem' }}>
                        <h4 className="card-title">📅 Fechas y Garantía</h4>
                        <div className="grid-2">
                            <div className="form-group">
                                <label className="form-label">Recepción</label>
                                <input type="date" className="form-input" name="reception_date" value={form.reception_date}
                                    onChange={e => setForm(f => ({ ...f, reception_date: e.target.value, acceptance_date: e.target.value }))} />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Aceptación</label>
                                <input type="date" className="form-input" name="acceptance_date" value={form.acceptance_date} onChange={handleChange} />
                            </div>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Años de Garantía</label>
                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                {[0, 1, 2, 3, 4].map(y => (
                                    <button
                                        key={y}
                                        type="button"
                                        className={`btn ${form.warranty_years === y ? 'btn-primary' : 'btn-secondary'}`}
                                        onClick={() => setForm(f => ({ ...f, warranty_years: y }))}
                                        style={{ padding: '0.5rem 1rem' }}
                                    >
                                        {y}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Fin Garantía</label>
                            <input type="date" className="form-input" name="warranty_end" value={form.warranty_end} onChange={handleChange} />
                        </div>
                    </div>
                </div>
            </div>

            <hr className="divider" />

            <div className="grid-2">
                {/* Registration Card */}
                <div className="card">
                    <h4 className="card-title">📝 Registro y Aceptación</h4>
                    <div className="form-group">
                        <label className="form-label">Nº Inventario</label>
                        <input type="text" className="form-input" name="main_inventory_number" value={form.main_inventory_number} onChange={handleChange} />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Nº Inventario Padre</label>
                        <input type="text" className="form-input" name="parent_inventory_number" value={form.parent_inventory_number} onChange={handleChange} />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Número Pedido</label>
                        <input type="text" className="form-input" name="order_number" value={form.order_number} onChange={handleChange} />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Importe (IVA inc.)</label>
                        <input type="text" className="form-input" name="amount_tax_included" value={form.amount_tax_included} onChange={handleChange} />
                    </div>
                </div>

                {/* Verifications Card */}
                <div className="card">
                    <h4 className="card-title">✅ Verificaciones</h4>
                    <div className="tabs">
                        <button className={`tab ${activeTab === 'general' ? 'active' : ''}`} onClick={() => setActiveTab('general')}>📋 General</button>
                        <button className={`tab ${activeTab === 'seguridad' ? 'active' : ''}`} onClick={() => setActiveTab('seguridad')}>🔒 Seguridad</button>
                        <button className={`tab ${activeTab === 'mantenimiento' ? 'active' : ''}`} onClick={() => setActiveTab('mantenimiento')}>🔧 Mant.</button>
                    </div>

                    {activeTab === 'general' && (
                        <>
                            <div className="checkbox-group"><input type="checkbox" className="checkbox-input" name="compliance" checked={form.compliance} onChange={handleChange} /><label className="checkbox-label">Cumple normativa</label></div>
                            <div className="checkbox-group"><input type="checkbox" className="checkbox-input" name="manuals_usage" checked={form.manuals_usage} onChange={handleChange} /><label className="checkbox-label">Manual Uso</label></div>
                            <div className="checkbox-group"><input type="checkbox" className="checkbox-input" name="manuals_tech" checked={form.manuals_tech} onChange={handleChange} /><label className="checkbox-label">Manual Técnico</label></div>
                            <div className="checkbox-group"><input type="checkbox" className="checkbox-input" name="order_accordance" checked={form.order_accordance} onChange={handleChange} /><label className="checkbox-label">Acorde a pedido</label></div>
                        </>
                    )}

                    {activeTab === 'seguridad' && (
                        <>
                            <div className="checkbox-group"><input type="checkbox" className="checkbox-input" name="patient_data" checked={form.patient_data} onChange={handleChange} /><label className="checkbox-label">Maneja datos pac.</label></div>
                            <div className="checkbox-group"><input type="checkbox" className="checkbox-input" name="backup_required" checked={form.backup_required} onChange={handleChange} /><label className="checkbox-label">Requiere copia seg.</label></div>
                            <div className="checkbox-group"><input type="checkbox" className="checkbox-input" name="requires_epis" checked={form.requires_epis} onChange={handleChange} /><label className="checkbox-label">Requiere EPIS</label></div>
                            <div className="checkbox-group"><input type="checkbox" className="checkbox-input" name="safe_to_use" checked={form.safe_to_use} onChange={handleChange} /><label className="checkbox-label">Seguro para uso</label></div>
                            <div className="checkbox-group"><input type="checkbox" className="checkbox-input" name="received_correctly" checked={form.received_correctly} onChange={handleChange} /><label className="checkbox-label">Recibido/Instalado correctamente</label></div>
                            <div className="checkbox-group"><input type="checkbox" className="checkbox-input" name="users_trained" checked={form.users_trained} onChange={handleChange} /><label className="checkbox-label">Usuarios formados</label></div>
                        </>
                    )}

                    {activeTab === 'mantenimiento' && (
                        <>
                            <div className="checkbox-group"><input type="checkbox" className="checkbox-input" name="preventive_maintenance" checked={form.preventive_maintenance} onChange={handleChange} /><label className="checkbox-label">Mant. Preventivo</label></div>
                            <div className="checkbox-group"><input type="checkbox" className="checkbox-input" name="maintenance_contract" checked={form.maintenance_contract} onChange={handleChange} /><label className="checkbox-label">Contrato Mant.</label></div>
                            <div className="form-group" style={{ marginTop: '1rem' }}>
                                <label className="form-label">Periodicidad</label>
                                <select className="form-select" name="periodicity" value={form.periodicity} onChange={handleChange}>
                                    <option>Anual</option>
                                    <option>Semestral</option>
                                    <option>Trimestral</option>
                                    <option>Bienal</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Estado del Equipo</label>
                                <div style={{ display: 'flex', gap: '0.5rem' }}>
                                    {['good', 'bad', 'obsolete'].map(status => (
                                        <button
                                            key={status}
                                            type="button"
                                            className={`btn ${form.equipment_status === status ? 'btn-primary' : 'btn-secondary'}`}
                                            onClick={() => setForm(f => ({ ...f, equipment_status: status }))}
                                            style={{ flex: 1, padding: '0.5rem' }}
                                        >
                                            {status === 'good' ? '✅ Bueno' : status === 'bad' ? '⚠️ Malo' : '🔴 Obsoleto'}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </div>

            <hr className="divider" />

            {/* Components */}
            <div className="card">
                <h4 className="card-title">🔧 Componentes del Equipo</h4>
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                    <button className="btn btn-secondary" onClick={() => addComponent(false)}>➕ Fila Vacía</button>
                    <button className="btn btn-secondary" onClick={() => addComponent(true)}>➕ Fila Marca: {form.brand || '...'}</button>
                </div>

                {form.components.length > 0 && (
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Nombre</th>
                                <th>Nº Inventario</th>
                                <th>Marca</th>
                                <th>Modelo</th>
                                <th>Nº Serie</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            {form.components.map((comp, i) => (
                                <tr key={i}>
                                    <td><input value={comp.name} onChange={e => handleComponentChange(i, 'name', e.target.value)} /></td>
                                    <td><input value={comp.inventory} onChange={e => handleComponentChange(i, 'inventory', e.target.value)} /></td>
                                    <td><input value={comp.brand} onChange={e => handleComponentChange(i, 'brand', e.target.value)} /></td>
                                    <td><input value={comp.model} onChange={e => handleComponentChange(i, 'model', e.target.value)} /></td>
                                    <td><input value={comp.serial} onChange={e => handleComponentChange(i, 'serial', e.target.value)} /></td>
                                    <td>
                                        <button className="btn btn-danger" style={{ padding: '0.25rem 0.5rem' }} onClick={() => removeComponent(i)}>🗑️</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}

                <div className="form-group" style={{ marginTop: '1rem' }}>
                    <label className="form-label">Observaciones</label>
                    <textarea className="form-textarea" name="observations" value={form.observations} onChange={handleChange} />
                </div>
            </div>

            <button
                className="btn btn-primary btn-full"
                onClick={handleSubmit}
                disabled={loading}
                style={{ marginTop: '1rem', padding: '1rem', fontSize: '1rem' }}
            >
                {loading ? '⏳ Generando...' : '🚀 GENERAR ACTA PDF'}
            </button>
        </div>
    );
}
