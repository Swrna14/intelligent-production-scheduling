import React, { useEffect, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { fetchDashboard, fetchDataset, runSchedule } from './services/api';
import './App.css';

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', marker: '01' },
  { id: 'orders', label: 'Production orders', marker: '02' },
  { id: 'machines', label: 'Machine floor', marker: '03' },
  { id: 'materials', label: 'Materials', marker: '04' },
];

const PRIORITY_COLORS = { urgent: '#ec694e', high: '#edb342', normal: '#78a99d' };
const EMPTY_SUMMARY = {
  total_products: 0,
  total_machines: 0,
  total_orders: 0,
  total_schedules: 0,
  total_materials: 0,
  urgent_orders: 0,
};

function formatNumber(value) {
  return new Intl.NumberFormat('en-US').format(value ?? 0);
}

function formatDate(value) {
  if (!value) return 'Not set';
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric' }).format(date);
}

function StatusBadge({ value }) {
  const status = (value || 'unknown').toLowerCase();
  return <span className={`status-badge status-${status}`}>{value || 'Unknown'}</span>;
}

function EmptyState({ title, detail }) {
  return <div className="empty-state"><span aria-hidden="true">—</span><strong>{title}</strong><p>{detail}</p></div>;
}

export default function App() {
  const [activeView, setActiveView] = useState('overview');
  const [summary, setSummary] = useState(EMPTY_SUMMARY);
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [machines, setMachines] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [materials, setMaterials] = useState([]);
  const [connection, setConnection] = useState('loading');
  const [loadError, setLoadError] = useState('');
  const [scale, setScale] = useState('starter');
  const [seed, setSeed] = useState('20261022');
  const [isRunning, setIsRunning] = useState(false);
  const [scheduleResult, setScheduleResult] = useState(null);
  const [scheduleError, setScheduleError] = useState('');
  const [lastUpdated, setLastUpdated] = useState(null);

  async function loadDashboard() {
    setConnection('loading');
    setLoadError('');
    try {
      const [nextSummary, orderPage, productPage, machinePage, schedulePage, materialPage] = await Promise.all([
        fetchDashboard(),
        fetchDataset('production_orders', 100),
        fetchDataset('products', 100),
        fetchDataset('machines', 100),
        fetchDataset('operation_schedules', 250),
        fetchDataset('materials', 100),
      ]);
      setSummary(nextSummary);
      setOrders(orderPage.items);
      setProducts(productPage.items);
      setMachines(machinePage.items);
      setSchedules(schedulePage.items);
      setMaterials(materialPage.items);
      setConnection('online');
      setLastUpdated(new Date());
    } catch (error) {
      setConnection('offline');
      setLoadError(error.message || 'The API could not be reached.');
    }
  }

  useEffect(() => { loadDashboard(); }, []);

  const productById = Object.fromEntries(products.map((product) => [product.product_id, product]));
  const machineById = Object.fromEntries(machines.map((machine) => [machine.machine_id, machine]));
  const priorityData = ['urgent', 'high', 'normal'].map((priority) => ({
    name: priority.charAt(0).toUpperCase() + priority.slice(1),
    value: orders.filter((order) => order.priority === priority).length,
    color: PRIORITY_COLORS[priority],
  })).filter((item) => item.value > 0);
  const machineLoad = machines.map((machine) => ({
    name: machine.machine_code,
    operations: schedules.filter((schedule) => schedule.machine_id === machine.machine_id).length,
  })).sort((left, right) => right.operations - left.operations).slice(0, 8);
  const rankedOrders = [...orders].sort((left, right) => {
    const rank = { urgent: 0, high: 1, normal: 2 };
    return (rank[left.priority] ?? 3) - (rank[right.priority] ?? 3)
      || new Date(left.due_date) - new Date(right.due_date);
  });
  const viewTitle = NAV_ITEMS.find((item) => item.id === activeView)?.label || 'Overview';

  async function handleScheduleRun(event) {
    event.preventDefault();
    setIsRunning(true);
    setScheduleError('');
    setScheduleResult(null);
    try {
      const result = await runSchedule({ scale, seed: Number(seed) });
      setScheduleResult({ ...result, runScale: scale, runSeed: Number(seed) });
      setActiveView('overview');
    } catch (error) {
      setScheduleError(error.message || 'The schedule could not be created.');
    } finally {
      setIsRunning(false);
    }
  }

  function openOptimizer() {
    setActiveView('overview');
    window.setTimeout(() => document.getElementById('schedule-panel')?.scrollIntoView({ behavior: 'smooth' }), 0);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#overview" onClick={() => setActiveView('overview')}>
          <span className="brand-symbol" aria-hidden="true"><i /><i /><i /></span>
          <span className="brand-copy"><strong>FORGE<span>/</span>OS</strong><small>PRODUCTION CONTROL</small></span>
        </a>
        <div className="plant-select"><span className="plant-dot" /><span><small>ACTIVE FACILITY</small><strong>North plant</strong></span><span className="plant-chevron">⌄</span></div>
        <nav className="primary-nav" aria-label="Primary navigation">
          <span className="nav-caption">WORKSPACE</span>
          {NAV_ITEMS.map((item) => (
            <button className={`nav-item ${activeView === item.id ? 'is-active' : ''}`} key={item.id} onClick={() => setActiveView(item.id)} type="button">
              <span className="nav-marker">{item.marker}</span><span>{item.label}</span>
              {activeView === item.id && <span className="nav-active-indicator" />}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-note">
            <span className="note-kicker">SCHEDULER</span><strong>Plan the next shift.</strong>
            <p>Generate a fresh production plan from the current order book.</p>
            <button type="button" onClick={openOptimizer}>Open optimizer <span>↗</span></button>
          </div>
          <div className="user-chip"><span className="user-avatar">OP</span><span><strong>Operations</strong><small>Planner workspace</small></span><span className="user-menu">•••</span></div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb"><span>WORKSPACE</span><b>/</b><strong>{viewTitle}</strong></div>
          <div className="topbar-actions">
            <span className={`connection-pill connection-${connection}`}><i />{connection === 'online' ? 'API connected' : connection === 'loading' ? 'Connecting' : 'API offline'}</span>
            <button className="icon-button" type="button" onClick={loadDashboard} aria-label="Refresh dashboard" title="Refresh dashboard"><span aria-hidden="true">↻</span></button>
            <span className="topbar-date">{new Intl.DateTimeFormat('en', { weekday: 'short', month: 'short', day: 'numeric' }).format(new Date())}</span>
          </div>
        </header>

        <div className="content-wrap">
          <section className="page-heading">
            <div><p className="eyebrow">NORTH PLANT <span>/</span> OPERATIONS</p><h1>{activeView === 'overview' ? 'Production overview' : viewTitle}</h1><p className="heading-subtitle">A live view of production activity, capacity, and order priorities.</p></div>
            <div className="heading-meta"><span className="meta-label">ORDER BOOK</span><strong>{connection === 'online' ? 'Starter · 20261022' : 'Waiting for API'}</strong><small>{lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : 'No refresh yet'}</small></div>
          </section>

          {loadError && <div className="alert-banner" role="alert"><span className="alert-icon">!</span><div><strong>Unable to load production data</strong><p>{loadError} Confirm the backend is running, then retry.</p></div><button type="button" onClick={loadDashboard}>Retry</button></div>}

          {activeView === 'overview' && (
            <>
              <section className="kpi-grid" aria-label="Production metrics">
                <MetricCard index="01" label="Production orders" value={summary.total_orders} foot={<><i className="tiny-dot dot-urgent" />{formatNumber(summary.urgent_orders)} urgent priority</>} accent />
                <MetricCard index="02" label="Scheduled operations" value={summary.total_schedules} foot="Across the current production plan" />
                <MetricCard index="03" label="Machines" value={summary.total_machines} foot={`${formatNumber(summary.total_products)} product families in scope`} />
                <MetricCard index="04" label="Material catalog" value={summary.total_materials} foot="Tracked production inputs" />
              </section>

              <section className="overview-grid">
                <article className="panel machine-panel">
                  <div className="panel-heading"><div><p className="eyebrow">RESOURCE LOAD</p><h2>Scheduled operations by machine</h2></div><button className="text-button" type="button" onClick={() => setActiveView('machines')}>View machines <span>↗</span></button></div>
                  {machineLoad.length ? <div className="chart-wrap machine-chart"><ResponsiveContainer width="100%" height="100%"><BarChart data={machineLoad} layout="vertical" margin={{ top: 4, right: 14, left: 4, bottom: 4 }} barCategoryGap={10}><CartesianGrid horizontal={false} stroke="#e7ebe6" /><XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: '#78817c', fontSize: 11 }} allowDecimals={false} /><YAxis type="category" dataKey="name" axisLine={false} tickLine={false} width={78} tick={{ fill: '#59635e', fontSize: 11, fontFamily: 'monospace' }} /><Tooltip cursor={{ fill: '#f0f3ef' }} contentStyle={{ border: '1px solid #dfe5df', borderRadius: 4, fontSize: 12 }} /><Bar dataKey="operations" name="Operations" fill="#315d50" radius={[0, 3, 3, 0]} maxBarSize={20} /></BarChart></ResponsiveContainer></div> : <EmptyState title="No machine data" detail="Machine assignments will appear when the API is available." />}
                  <div className="chart-legend"><span><i className="legend-square legend-green" />Scheduled operations</span><span>Top {machineLoad.length} machines</span></div>
                </article>

                <article className="panel priority-panel">
                  <div className="panel-heading"><div><p className="eyebrow">ORDER BOOK</p><h2>Priority mix</h2></div><span className="panel-total">{formatNumber(orders.length)} orders</span></div>
                  {priorityData.length ? <div className="priority-content"><div className="donut-wrap"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={priorityData} dataKey="value" nameKey="name" innerRadius="66%" outerRadius="88%" paddingAngle={3} stroke="none">{priorityData.map((item) => <Cell key={item.name} fill={item.color} />)}</Pie><Tooltip contentStyle={{ border: '1px solid #dfe5df', borderRadius: 4, fontSize: 12 }} /></PieChart></ResponsiveContainer><div className="donut-center"><strong>{formatNumber(orders.length)}</strong><small>orders</small></div></div><div className="priority-legend">{priorityData.map((item) => <div className="priority-row" key={item.name}><span className="priority-name"><i style={{ backgroundColor: item.color }} />{item.name}</span><strong>{formatNumber(item.value)}</strong></div>)}</div></div> : <EmptyState title="No priority data" detail="Order priorities will appear here." />}
                  <div className="priority-foot"><span>URGENT + HIGH</span><strong>{formatNumber(priorityData.filter((item) => ['Urgent', 'High'].includes(item.name)).reduce((total, item) => total + item.value, 0))}</strong><small>orders need attention</small></div>
                </article>
              </section>

              <section className="lower-grid">
                <article className="panel order-panel"><div className="panel-heading"><div><p className="eyebrow">ACTION QUEUE</p><h2>Orders to watch</h2></div><button className="text-button" type="button" onClick={() => setActiveView('orders')}>All orders <span>↗</span></button></div><OrderTable orders={rankedOrders.slice(0, 6)} products={productById} compact /></article>
                <SchedulePanel scale={scale} setScale={setScale} seed={seed} setSeed={setSeed} isRunning={isRunning} onRun={handleScheduleRun} result={scheduleResult} error={scheduleError} machineById={machineById} />
              </section>
            </>
          )}

          {activeView === 'orders' && <section className="panel data-panel"><div className="panel-heading"><div><p className="eyebrow">ORDER BOOK</p><h2>Production orders</h2></div><span className="panel-total">{formatNumber(summary.total_orders)} total · first {orders.length} loaded</span></div><OrderTable orders={rankedOrders} products={productById} /></section>}
          {activeView === 'machines' && <section className="panel data-panel"><div className="panel-heading"><div><p className="eyebrow">RESOURCE DIRECTORY</p><h2>Machine floor</h2></div><span className="panel-total">{formatNumber(machines.length)} resources</span></div><MachineTable machines={machines} schedules={schedules} /></section>}
          {activeView === 'materials' && <section className="panel data-panel"><div className="panel-heading"><div><p className="eyebrow">INPUT CATALOG</p><h2>Materials</h2></div><span className="panel-total">{formatNumber(materials.length)} materials</span></div><MaterialTable materials={materials} /></section>}

          <footer className="page-footer"><span>FORGE/OS <b>·</b> PRODUCTION CONTROL</span><span>Scheduling data is generated from the active dataset.</span></footer>
        </div>
      </main>
    </div>
  );
}

function MetricCard({ index, label, value, foot, accent = false }) {
  return <article className={`kpi-card ${accent ? 'kpi-accent' : ''}`}><div className="kpi-top"><span>{label}</span><span className="kpi-index">{index}</span></div><strong className="kpi-value">{formatNumber(value)}</strong><div className="kpi-foot">{foot}</div></article>;
}

function OrderTable({ orders, products, compact = false }) {
  if (!orders.length) return <EmptyState title="No orders to show" detail="Check the API connection or refresh the dataset." />;
  return <div className="table-scroll"><table className="data-table"><thead><tr><th>ORDER</th><th>PRODUCT</th><th>QUANTITY</th><th>PRIORITY</th><th>DUE DATE</th><th>STATUS</th></tr></thead><tbody>{orders.map((order) => <tr key={order.order_id}><td><strong className="table-primary">{order.order_code}</strong></td><td><span className="muted-cell">{products[order.product_id]?.product_name || `Product ${order.product_id}`}</span></td><td className="number-cell">{formatNumber(order.quantity)}</td><td><span className={`priority-tag priority-${order.priority}`}>{order.priority}</span></td><td>{formatDate(order.due_date)}</td><td><StatusBadge value={order.status} /></td></tr>)}</tbody></table>{compact && <div className="table-bottom-note">Showing highest-priority orders first</div>}</div>;
}

function MachineTable({ machines, schedules }) {
  if (!machines.length) return <EmptyState title="No machines to show" detail="Machine resources will appear when the API is available." />;
  return <div className="table-scroll"><table className="data-table"><thead><tr><th>MACHINE</th><th>TYPE</th><th>LOCATION</th><th>CAPACITY / SHIFT</th><th>SCHEDULED OPS</th><th>STATUS</th></tr></thead><tbody>{machines.map((machine) => <tr key={machine.machine_id}><td><strong className="table-primary">{machine.machine_code}</strong><small className="table-secondary">{machine.machine_name}</small></td><td>{machine.machine_type}</td><td>{machine.location}</td><td className="number-cell">{machine.capacity_per_shift}</td><td className="number-cell">{schedules.filter((row) => row.machine_id === machine.machine_id).length}</td><td><StatusBadge value={machine.status} /></td></tr>)}</tbody></table></div>;
}

function MaterialTable({ materials }) {
  if (!materials.length) return <EmptyState title="No materials to show" detail="Material catalog records will appear when the API is available." />;
  return <div className="table-scroll"><table className="data-table"><thead><tr><th>MATERIAL</th><th>DESCRIPTION</th><th>UNIT</th><th>REORDER POINT</th><th>LEAD TIME</th></tr></thead><tbody>{materials.map((material) => <tr key={material.material_id}><td><strong className="table-primary">{material.material_code}</strong></td><td>{material.material_name}</td><td>{material.unit_of_measure}</td><td className="number-cell">{formatNumber(material.reorder_point)}</td><td className="number-cell">{material.lead_time_days} days</td></tr>)}</tbody></table></div>;
}

function SchedulePanel({ scale, setScale, seed, setSeed, isRunning, onRun, result, error, machineById }) {
  return <article className="panel schedule-panel" id="schedule-panel"><div className="panel-heading"><div><p className="eyebrow">OPTIMIZATION ENGINE</p><h2>Build a schedule</h2></div><span className="engine-status"><i />READY</span></div>
    <p className="schedule-description">Run the scheduler against a reproducible production dataset.</p>
    <form className="schedule-form" onSubmit={onRun}><label className="field-label" htmlFor="dataset-scale">DATASET SIZE</label><select id="dataset-scale" value={scale} onChange={(event) => setScale(event.target.value)}><option value="starter">Starter</option><option value="full">Full</option></select><label className="field-label" htmlFor="dataset-seed">RANDOM SEED</label><input id="dataset-seed" type="number" min="0" value={seed} onChange={(event) => setSeed(event.target.value)} required /><button className="run-button" type="submit" disabled={isRunning}><span aria-hidden="true">{isRunning ? '◌' : '▶'}</span>{isRunning ? 'Optimizing…' : 'Run optimizer'}</button></form>
    {error && <p className="inline-error" role="alert">{error}</p>}
    {result ? <div className="result-block" aria-live="polite"><div className="result-header"><span className="result-check">{result.feasible ? '✓' : '!'}</span><div><strong>{result.feasible ? 'Schedule generated' : 'No feasible schedule'}</strong><small>{result.runScale} dataset · seed {result.runSeed}. {result.reason}</small></div></div><div className="result-stats"><span><strong>{result.assignments.length}</strong><small>assignments</small></span><span><strong>{result.objective_value == null ? '—' : formatNumber(Math.round(result.objective_value))}</strong><small>objective</small></span></div>{result.assignments.length > 0 && <div className="assignment-list">{result.assignments.slice(0, 4).map((assignment) => <div className="assignment-row" key={`${assignment.job_id}-${assignment.machine_id}`}><strong>Order {assignment.job_id}</strong><span>{machineById[assignment.machine_id]?.machine_code || `Machine ${assignment.machine_id}`}</span><StatusBadge value={assignment.status} /></div>)}{result.assignments.length > 4 && <small className="more-assignments">+{result.assignments.length - 4} more assignments</small>}</div>}</div> : !error && <div className="schedule-footnote"><span aria-hidden="true">✳</span><span>Results are deterministic for the same scale and seed.</span></div>}
  </article>;
}
