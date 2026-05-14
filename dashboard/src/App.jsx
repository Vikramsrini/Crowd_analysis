import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

const API = 'http://localhost:8000';

function App() {
  const [stats, setStats] = useState({ count: 0, status: 'initializing' });
  const [activeTab, setActiveTab] = useState('gallery');
  const [images, setImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [showHeatmap, setShowHeatmap] = useState('yolo');
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 12;

  // Poll stats
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API}/stats`);
        const data = await res.json();
        setStats(data);
      } catch {
        setStats(s => ({ ...s, status: 'offline' }));
      }
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Load gallery images
  useEffect(() => {
    fetch(`${API}/gallery/images`)
      .then(r => r.json())
      .then(data => setImages(data.images || []))
      .catch(() => {});
  }, []);

  const analyzeImage = useCallback(async (imageId) => {
    setSelectedImage(imageId);
    setAnalysis(null);
    setAnalyzing(true);
    try {
      const res = await fetch(`${API}/gallery/analyze/${imageId}`);
      const data = await res.json();
      setAnalysis(data);
    } catch (e) {
      console.error('Analysis failed:', e);
    }
    setAnalyzing(false);
  }, []);

  const pagedImages = images.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  const totalPages = Math.ceil(images.length / PAGE_SIZE);

  return (
    <div className="dashboard-container animate-fade-in">
      <header className="header">
        <h1>CrowdInsight AI</h1>
        <div className="tab-bar">
          <button
            className={`tab-btn ${activeTab === 'gallery' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('gallery')}
          >
            📸 Image Gallery
          </button>
          <button
            className={`tab-btn ${activeTab === 'live' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('live')}
          >
            🎥 Live Stream
          </button>
        </div>
        <div className={`badge ${stats.status === 'active' ? 'badge-active' : 'badge-offline'}`}>
          {stats.status.toUpperCase()}
        </div>
      </header>

      {activeTab === 'live' && (
        <main className="main-content">
          <section className="stream-viewer">
            {stats.status === 'active' ? (
              <img src={`${API}/video_feed`} alt="Crowd Analysis Stream" />
            ) : (
              <div className="loading-state"><p>Awaiting Stream...</p></div>
            )}
          </section>
          <aside className="stats-panel">
            <div className="stat-card">
              <div className="stat-label">Tracked Persons</div>
              <div className="stat-value">{stats.count}</div>
              <div className="stat-sub">Active Tracks (ByteTrack)</div>
            </div>
            <div className="stat-card accent-card">
              <div className="stat-label" style={{ color: '#818cf8' }}>Pipeline</div>
              <div className="stat-value" style={{ fontSize: '1.2rem' }}>YOLOv8 + ByteTrack</div>
              <div className="stat-sub">Detection → Tracking → ROI → Behavior → Alerts</div>
            </div>
            {stats.roi_counts && Object.keys(stats.roi_counts).length > 0 && (
              <div className="stat-card">
                <div className="stat-label">ROI Zones</div>
                {Object.entries(stats.roi_counts).map(([zone, count]) => (
                  <div key={zone} className="roi-row">
                    <span className="roi-name">{zone}</span>
                    <span className="roi-count">{count}</span>
                  </div>
                ))}
              </div>
            )}
            {stats.alerts && stats.alerts.length > 0 && (
              <div className="stat-card alert-card">
                <div className="stat-label" style={{ color: '#f87171' }}>Alerts</div>
                {stats.alerts.map((msg, i) => (
                  <div key={i} className="alert-row">{msg}</div>
                ))}
              </div>
            )}
          </aside>
        </main>
      )}

      {activeTab === 'gallery' && (
        <main className="gallery-layout">
          {/* Analysis Panel */}
          {selectedImage && (
            <section className="analysis-panel animate-fade-in">
              {analyzing ? (
                <div className="loading-state" style={{ minHeight: 300 }}>
                  <p>Analyzing crowd density...</p>
                </div>
              ) : analysis ? (
                <>
                  <div className="analysis-header">
                    <h2>IMG_{analysis.image_id}.jpg</h2>
                    <div className="analysis-counts">
                      <div className="count-badge yolo-badge">
                        <span className="count-number-sm">{analysis.yolo_count}</span>
                        <span className="count-tag">YOLOv8</span>
                      </div>
                      <div className="count-badge density-badge">
                        <span className="count-number-sm">{analysis.density_count}</span>
                        <span className="count-tag">MCNN</span>
                      </div>
                    </div>
                  </div>
                  <div className="analysis-images">
                    <div className="toggle-bar">
                      <button
                        className={`toggle-btn ${showHeatmap === 'original' ? 'toggle-active' : ''}`}
                        onClick={() => setShowHeatmap('original')}
                      >Original</button>
                      <button
                        className={`toggle-btn ${showHeatmap === 'yolo' ? 'toggle-active' : ''}`}
                        onClick={() => setShowHeatmap('yolo')}
                      >🎯 YOLOv8</button>
                      <button
                        className={`toggle-btn ${showHeatmap === 'density' ? 'toggle-active' : ''}`}
                        onClick={() => setShowHeatmap('density')}
                      >🔥 Density Map</button>
                    </div>
                    <div className="analysis-image-viewer">
                      <img
                        src={`data:image/jpeg;base64,${
                          showHeatmap === 'yolo' ? analysis.yolo_overlay :
                          showHeatmap === 'density' ? analysis.heatmap_overlay :
                          analysis.original
                        }`}
                        alt={showHeatmap === 'yolo' ? 'YOLO Detection' : showHeatmap === 'density' ? 'Density Heatmap' : 'Original'}
                      />
                    </div>
                  </div>
                  <div className="crowd-level-row">
                    <span className={`crowd-level-badge crowd-level-${analysis.crowd_level_color}`}>
                      {analysis.crowd_level === 'Very Sparse' && '🟢'}
                      {analysis.crowd_level === 'Sparse' && '🟡'}
                      {analysis.crowd_level === 'Moderate' && '🟠'}
                      {analysis.crowd_level === 'Dense' && '🔴'}
                      {analysis.crowd_level === 'Very Dense' && '🚨'}
                      {' '}{analysis.crowd_level}
                    </span>
                    <span className="crowd-level-label">Crowd Level (from density map)</span>
                  </div>

                  <div className="accuracy-section">
                    <div className="accuracy-header">
                      <span className="accuracy-title">MCNN Accuracy Estimate</span>
                      <span className="accuracy-pct">{analysis.accuracy_pct}%</span>
                    </div>
                    <div className="accuracy-bar-bg">
                      <div className="accuracy-bar-fill" style={{ width: `${Math.min(analysis.accuracy_pct, 100)}%` }} />
                    </div>
                    <div className="accuracy-note">
                      Expected count range: <strong>{analysis.count_range}</strong>
                      &nbsp;&middot;&nbsp;Model MAPE: ±22.8% &nbsp;&middot;&nbsp; MAE: ±{analysis.model_mae}
                    </div>
                  </div>

                  <div className="analysis-stats">
                    <div className="mini-stat">
                      <span className="mini-label">Density Min</span>
                      <span className="mini-value">{analysis.density_min.toFixed(4)}</span>
                    </div>
                    <div className="mini-stat">
                      <span className="mini-label">Density Max</span>
                      <span className="mini-value">{analysis.density_max.toFixed(4)}</span>
                    </div>
                    <div className="mini-stat">
                      <span className="mini-label">Density Mean</span>
                      <span className="mini-value">{analysis.density_mean.toFixed(4)}</span>
                    </div>
                  </div>
                </>
              ) : null}
            </section>
          )}

          {/* Thumbnail Grid */}
          <section className="gallery-section">
            <div className="gallery-header">
              <h2>ShanghaiTech Part B — Test Images</h2>
              <span className="image-count">{images.length} images</span>
            </div>
            <div className="gallery-grid">
              {pagedImages.map(img => (
                <div
                  key={img.id}
                  className={`gallery-thumb ${selectedImage === img.id ? 'thumb-selected' : ''}`}
                  onClick={() => analyzeImage(img.id)}
                >
                  <img src={`${API}/gallery/image/${img.id}`} alt={`IMG_${img.id}`} loading="lazy" />
                  <div className="thumb-label">IMG_{img.id}</div>
                </div>
              ))}
            </div>
            {totalPages > 1 && (
              <div className="pagination">
                <button className="page-btn" onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}>← Prev</button>
                <span className="page-info">{page + 1} / {totalPages}</span>
                <button className="page-btn" onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1}>Next →</button>
              </div>
            )}
          </section>
        </main>
      )}
    </div>
  );
}

export default App;
