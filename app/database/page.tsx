'use client';

import { useState, useEffect } from 'react';

interface Service {
    manager?: string;
    unit?: string;
    floor?: string;
    hole?: string;
    center_name?: string;
    center_code?: string;
}

interface Model {
    description?: string;
    brand?: string;
    provider?: string;
    contact?: string;
}

interface Memory {
    defaults: {
        services: Record<string, Service>;
        models: Record<string, Model>;
    };
}

export default function DatabasePage() {
    const [memory, setMemory] = useState<Memory>({ defaults: { services: {}, models: {} } });
    const [activeTab, setActiveTab] = useState<'services' | 'models'>('services');
    const [message, setMessage] = useState<{ type: 'success' | 'warning' | 'error'; text: string } | null>(null);

    // Service form
    const [newService, setNewService] = useState({ name: '', manager: '', unit: '', floor: '', hole: '', center_name: 'POLICLINICA GIPUZKOA', center_code: 'T05-POLGIP-HOS' });
    const [editService, setEditService] = useState<string>('');
    const [editServiceData, setEditServiceData] = useState<Service>({});

    // Model form
    const [newModel, setNewModel] = useState({ name: '', description: '', brand: '', provider: '', contact: '' });
    const [editModel, setEditModel] = useState<string>('');
    const [editModelData, setEditModelData] = useState<Model>({});

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const res = await fetch('/api/data');
            const data = await res.json();
            setMemory(data);
        } catch (e) {
            console.error(e);
        }
    };

    const saveData = async (data: Memory) => {
        try {
            await fetch('/api/data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            setMemory(data);
        } catch (e) {
            console.error(e);
        }
    };

    // Service handlers
    const handleCreateService = async () => {
        if (!newService.name) {
            setMessage({ type: 'error', text: 'El nombre del servicio es obligatorio.' });
            return;
        }
        const updated = { ...memory };
        updated.defaults.services[newService.name] = {
            manager: newService.manager,
            unit: newService.unit,
            floor: newService.floor,
            hole: newService.hole,
            center_name: newService.center_name,
            center_code: newService.center_code,
        };
        await saveData(updated);
        setMessage({ type: 'success', text: `✅ ¡Servicio '${newService.name}' registrado con éxito!` });
        setNewService({ name: '', manager: '', unit: '', floor: '', hole: '', center_name: 'POLICLINICA GIPUZKOA', center_code: 'T05-POLGIP-HOS' });
    };

    const handleUpdateService = async () => {
        if (!editService) return;
        const updated = { ...memory };
        updated.defaults.services[editService] = editServiceData;
        await saveData(updated);
        setMessage({ type: 'success', text: `✅ Servicio '${editService}' actualizado.` });
    };

    const handleDeleteService = async () => {
        if (!editService) return;
        const updated = { ...memory };
        delete updated.defaults.services[editService];
        await saveData(updated);
        setMessage({ type: 'warning', text: `Servicio '${editService}' eliminado.` });
        setEditService('');
        setEditServiceData({});
    };

    // Model handlers
    const handleCreateModel = async () => {
        if (!newModel.name) {
            setMessage({ type: 'error', text: 'El nombre del modelo es obligatorio.' });
            return;
        }
        const updated = { ...memory };
        updated.defaults.models[newModel.name] = {
            description: newModel.description,
            brand: newModel.brand,
            provider: newModel.provider,
            contact: newModel.contact,
        };
        await saveData(updated);
        setMessage({ type: 'success', text: `📦 ¡Modelo '${newModel.name}' registrado con éxito!` });
        setNewModel({ name: '', description: '', brand: '', provider: '', contact: '' });
    };

    const handleUpdateModel = async () => {
        if (!editModel) return;
        const updated = { ...memory };
        updated.defaults.models[editModel] = editModelData;
        await saveData(updated);
        setMessage({ type: 'success', text: `✅ Modelo '${editModel}' actualizado.` });
    };

    const handleDeleteModel = async () => {
        if (!editModel) return;
        const updated = { ...memory };
        delete updated.defaults.models[editModel];
        await saveData(updated);
        setMessage({ type: 'warning', text: `Modelo '${editModel}' eliminado.` });
        setEditModel('');
        setEditModelData({});
    };

    const serviceList = Object.keys(memory.defaults.services).sort();
    const modelList = Object.keys(memory.defaults.models).sort();

    return (
        <div>
            <h1>💾 Gestión de Base de Datos</h1>

            {message && (
                <div className={`alert alert-${message.type}`}>
                    {message.text}
                </div>
            )}

            <div className="tabs">
                <button className={`tab ${activeTab === 'services' ? 'active' : ''}`} onClick={() => setActiveTab('services')}>
                    🏢 Servicios y Plantas
                </button>
                <button className={`tab ${activeTab === 'models' ? 'active' : ''}`} onClick={() => setActiveTab('models')}>
                    📦 Modelos y Equipos
                </button>
            </div>

            {activeTab === 'services' && (
                <>
                    {/* Add New Service */}
                    <div className="expander">
                        <div className="expander-header">➕ AÑADIR NUEVO SERVICIO</div>
                        <div className="expander-content">
                            <div className="form-group">
                                <label className="form-label">Nombre del Servicio (Ej: RADIOLOGÍA)</label>
                                <input type="text" className="form-input" value={newService.name} onChange={e => setNewService({ ...newService, name: e.target.value })} />
                            </div>
                            <div className="grid-2">
                                <div className="form-group">
                                    <label className="form-label">Responsable</label>
                                    <input type="text" className="form-input" value={newService.manager} onChange={e => setNewService({ ...newService, manager: e.target.value })} />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Unidad</label>
                                    <input type="text" className="form-input" value={newService.unit} onChange={e => setNewService({ ...newService, unit: e.target.value })} />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Planta</label>
                                    <input type="text" className="form-input" value={newService.floor} onChange={e => setNewService({ ...newService, floor: e.target.value })} />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Hueco</label>
                                    <input type="text" className="form-input" value={newService.hole} onChange={e => setNewService({ ...newService, hole: e.target.value })} />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Centro</label>
                                    <input type="text" className="form-input" value={newService.center_name} onChange={e => setNewService({ ...newService, center_name: e.target.value })} />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Cód. Centro</label>
                                    <input type="text" className="form-input" value={newService.center_code} onChange={e => setNewService({ ...newService, center_code: e.target.value })} />
                                </div>
                            </div>
                            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                                <button className="btn btn-primary" onClick={handleCreateService}>✨ Crear Servicio</button>
                                <button className="btn btn-secondary" onClick={() => setNewService({ name: '', manager: '', unit: '', floor: '', hole: '', center_name: 'POLICLINICA GIPUZKOA', center_code: 'T05-POLGIP-HOS' })}>🧹 Limpiar</button>
                            </div>
                        </div>
                    </div>

                    {/* Edit Services */}
                    <div className="card">
                        <h4 className="card-title">🏢 Editar Servicios Existentes</h4>
                        {serviceList.length === 0 ? (
                            <p style={{ color: 'var(--q-text-muted)' }}>No hay servicios guardados todavía.</p>
                        ) : (
                            <>
                                <div className="form-group">
                                    <label className="form-label">Selecciona para editar</label>
                                    <select className="form-select" value={editService} onChange={e => {
                                        setEditService(e.target.value);
                                        setEditServiceData(memory.defaults.services[e.target.value] || {});
                                    }}>
                                        <option value="">--</option>
                                        {serviceList.map(s => <option key={s} value={s}>{s}</option>)}
                                    </select>
                                </div>

                                {editService && (
                                    <>
                                        <h3 style={{ marginTop: '1.5rem' }}>Servicio: {editService}</h3>
                                        <div className="grid-2">
                                            <div className="form-group">
                                                <label className="form-label">Responsable</label>
                                                <input type="text" className="form-input" value={editServiceData.manager || ''} onChange={e => setEditServiceData({ ...editServiceData, manager: e.target.value })} />
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">Unidad</label>
                                                <input type="text" className="form-input" value={editServiceData.unit || ''} onChange={e => setEditServiceData({ ...editServiceData, unit: e.target.value })} />
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">Planta</label>
                                                <input type="text" className="form-input" value={editServiceData.floor || ''} onChange={e => setEditServiceData({ ...editServiceData, floor: e.target.value })} />
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">Hueco</label>
                                                <input type="text" className="form-input" value={editServiceData.hole || ''} onChange={e => setEditServiceData({ ...editServiceData, hole: e.target.value })} />
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">Centro</label>
                                                <input type="text" className="form-input" value={editServiceData.center_name || ''} onChange={e => setEditServiceData({ ...editServiceData, center_name: e.target.value })} />
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">Cód. Centro</label>
                                                <input type="text" className="form-input" value={editServiceData.center_code || ''} onChange={e => setEditServiceData({ ...editServiceData, center_code: e.target.value })} />
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                                            <button className="btn btn-primary" onClick={handleUpdateService}>💾 Guardar Cambios</button>
                                            <button className="btn btn-danger" onClick={handleDeleteService}>🗑️ Borrar Servicio</button>
                                        </div>
                                    </>
                                )}
                            </>
                        )}
                    </div>
                </>
            )}

            {activeTab === 'models' && (
                <>
                    {/* Add New Model */}
                    <div className="expander">
                        <div className="expander-header">➕ AÑADIR NUEVA REFERENCIA / MODELO</div>
                        <div className="expander-content">
                            <div className="form-group">
                                <label className="form-label">Nombre del Modelo / Referencia</label>
                                <input type="text" className="form-input" value={newModel.name} onChange={e => setNewModel({ ...newModel, name: e.target.value })} />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Descripción</label>
                                <input type="text" className="form-input" value={newModel.description} onChange={e => setNewModel({ ...newModel, description: e.target.value })} />
                            </div>
                            <div className="grid-2">
                                <div className="form-group">
                                    <label className="form-label">Marca</label>
                                    <input type="text" className="form-input" value={newModel.brand} onChange={e => setNewModel({ ...newModel, brand: e.target.value })} />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Proveedor</label>
                                    <input type="text" className="form-input" value={newModel.provider} onChange={e => setNewModel({ ...newModel, provider: e.target.value })} />
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Contacto</label>
                                <input type="text" className="form-input" value={newModel.contact} onChange={e => setNewModel({ ...newModel, contact: e.target.value })} />
                            </div>
                            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                                <button className="btn btn-primary" onClick={handleCreateModel}>✨ Crear Modelo</button>
                                <button className="btn btn-secondary" onClick={() => setNewModel({ name: '', description: '', brand: '', provider: '', contact: '' })}>🧹 Limpiar</button>
                            </div>
                        </div>
                    </div>

                    {/* Edit Models */}
                    <div className="card">
                        <h4 className="card-title">📦 Editar Modelos Existentes</h4>
                        {modelList.length === 0 ? (
                            <p style={{ color: 'var(--q-text-muted)' }}>No hay modelos guardados todavía.</p>
                        ) : (
                            <>
                                <div className="form-group">
                                    <label className="form-label">Selecciona para editar</label>
                                    <select className="form-select" value={editModel} onChange={e => {
                                        setEditModel(e.target.value);
                                        setEditModelData(memory.defaults.models[e.target.value] || {});
                                    }}>
                                        <option value="">--</option>
                                        {modelList.map(m => <option key={m} value={m}>{m}</option>)}
                                    </select>
                                </div>

                                {editModel && (
                                    <>
                                        <h3 style={{ marginTop: '1.5rem' }}>Modelo: {editModel}</h3>
                                        <div className="form-group">
                                            <label className="form-label">Descripción</label>
                                            <input type="text" className="form-input" value={editModelData.description || ''} onChange={e => setEditModelData({ ...editModelData, description: e.target.value })} />
                                        </div>
                                        <div className="grid-2">
                                            <div className="form-group">
                                                <label className="form-label">Marca</label>
                                                <input type="text" className="form-input" value={editModelData.brand || ''} onChange={e => setEditModelData({ ...editModelData, brand: e.target.value })} />
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">Proveedor</label>
                                                <input type="text" className="form-input" value={editModelData.provider || ''} onChange={e => setEditModelData({ ...editModelData, provider: e.target.value })} />
                                            </div>
                                        </div>
                                        <div className="form-group">
                                            <label className="form-label">Contacto</label>
                                            <input type="text" className="form-input" value={editModelData.contact || ''} onChange={e => setEditModelData({ ...editModelData, contact: e.target.value })} />
                                        </div>
                                        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                                            <button className="btn btn-primary" onClick={handleUpdateModel}>💾 Guardar Cambios</button>
                                            <button className="btn btn-danger" onClick={handleDeleteModel}>🗑️ Borrar Modelo</button>
                                        </div>
                                    </>
                                )}
                            </>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}
