'use client';

import { useState, useEffect } from 'react';
import ServiceCombobox from '@/components/ServiceCombobox';
import ModelCombobox from '@/components/ModelCombobox';

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
    property: string;
    main_inventory_number: string;
    parent_inventory_number: string;
    baja_date: string;
    justification_report: string;
    work_order_number: string;
    repair_budget: boolean;
    replacement_budget: boolean;
    sat_report: boolean;
    other_docs: boolean;
    data_cleaned: boolean;
    observations: string;
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
    property: '',
    main_inventory_number: 'INV-',
    parent_inventory_number: '',
    baja_date: new Date().toISOString().split('T')[0],
    justification_report: '',
    work_order_number: '',
    repair_budget: true,
    replacement_budget: true,
    sat_report: true,
    other_docs: true,
    data_cleaned: true,
    observations: '',
};

export default function BajaPage() {
    const [form, setForm] = useState<FormData>(DEFAULT_FORM);
    const [memory, setMemory] = useState<any>({ defaults: { services: {}, models: {} } });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    useEffect(() => {
        fetch('/api/data')
            .then(res => res.json())
            .then(data => setMemory(data))
            .catch(console.error);
    }, []);

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
            }));
        } else {
            setForm(f => ({ ...f, model: modelName }));
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value, type } = e.target;
        if (type === 'checkbox') {
            setForm(f => ({ ...f, [name]: (e.target as HTMLInputElement).checked }));
        } else {
            setForm(f => ({ ...f, [name]: value }));
        }
    };

    const handleClear = () => {
        setForm(DEFAULT_FORM);
        setMessage(null);
    };

    const formatDate = (dateStr: string) => {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleDateString('es-ES');
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
                        baja_date: formatDate(form.baja_date),
                    },
                    reportType: 'baja',
                }),
            });

            if (!response.ok) throw new Error('Error generating PDF');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Acta_Baja_${form.serial_number || 'EQUIPO'}.pdf`;
            a.click();
            window.URL.revokeObjectURL(url);

            setMessage({ type: 'success', text: '✅ Acta de Baja generada con éxito.' });
        } catch (error) {
            console.error(error);
            setMessage({ type: 'error', text: '❌ Error generando el PDF.' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h1>🗑️ Nueva Acta de Baja</h1>
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
                        <label className="form-label">Propiedad</label>
                        <input type="text" className="form-input" name="property" value={form.property} onChange={handleChange} />
                    </div>

                    <div className="grid-2">
                        <div className="form-group">
                            <label className="form-label">Nº Inventario</label>
                            <input type="text" className="form-input" name="main_inventory_number" value={form.main_inventory_number} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Nº Inventario Padre</label>
                            <input type="text" className="form-input" name="parent_inventory_number" value={form.parent_inventory_number} onChange={handleChange} />
                        </div>
                    </div>
                </div>
            </div>

            <hr className="divider" />

            <div className="grid-2">
                {/* Justification Card */}
                <div className="card">
                    <h4 className="card-title">📑 Informe Justificativo</h4>
                    <div className="form-group">
                        <label className="form-label">Fecha Baja</label>
                        <input type="date" className="form-input" name="baja_date" value={form.baja_date} onChange={handleChange} />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Justificación de la Baja</label>
                        <textarea
                            className="form-textarea"
                            name="justification_report"
                            value={form.justification_report}
                            onChange={handleChange}
                            style={{ minHeight: '150px' }}
                        />
                    </div>
                </div>

                {/* Acceptance Card */}
                <div className="card">
                    <h4 className="card-title">✅ Aceptación de la Baja</h4>
                    <div className="form-group">
                        <label className="form-label">Número Orden de Trabajo</label>
                        <input type="text" className="form-input" name="work_order_number" value={form.work_order_number} onChange={handleChange} />
                    </div>

                    <div className="grid-2">
                        <div>
                            <div className="checkbox-group">
                                <input type="checkbox" className="checkbox-input" name="repair_budget" checked={form.repair_budget} onChange={handleChange} />
                                <label className="checkbox-label">Presupuesto reparación</label>
                            </div>
                            <div className="checkbox-group">
                                <input type="checkbox" className="checkbox-input" name="replacement_budget" checked={form.replacement_budget} onChange={handleChange} />
                                <label className="checkbox-label">Presupuesto reposición</label>
                            </div>
                        </div>
                        <div>
                            <div className="checkbox-group">
                                <input type="checkbox" className="checkbox-input" name="sat_report" checked={form.sat_report} onChange={handleChange} />
                                <label className="checkbox-label">SAT oficial</label>
                            </div>
                            <div className="checkbox-group">
                                <input type="checkbox" className="checkbox-input" name="other_docs" checked={form.other_docs} onChange={handleChange} />
                                <label className="checkbox-label">Otros documentos</label>
                            </div>
                        </div>
                    </div>

                    <div className="checkbox-group" style={{ marginTop: '1rem' }}>
                        <input type="checkbox" className="checkbox-input" name="data_cleaned" checked={form.data_cleaned} onChange={handleChange} />
                        <label className="checkbox-label">Limpieza de datos realizada</label>
                    </div>

                    <div className="form-group" style={{ marginTop: '1rem' }}>
                        <label className="form-label">Observaciones</label>
                        <textarea className="form-textarea" name="observations" value={form.observations} onChange={handleChange} />
                    </div>
                </div>
            </div>

            <button
                className="btn btn-primary btn-full"
                onClick={handleSubmit}
                disabled={loading}
                style={{ marginTop: '1rem', padding: '1rem', fontSize: '1rem' }}
            >
                {loading ? '⏳ Generando...' : '🚀 GENERAR ACTA DE BAJA (PDF)'}
            </button>
        </div>
    );
}
