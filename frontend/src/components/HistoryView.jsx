import React, { useState, useEffect } from 'react';
import {
  History,
  Search,
  Filter,
  Download,
  Trash2,
  RotateCw,
  Bookmark,
  BookmarkCheck,
  ArrowRight,
  RefreshCw,
  FileText,
  AlertTriangle
} from 'lucide-react';
import { api } from '../services/api';

export default function HistoryView({ onViewVerification, onNewVerification }) {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [days, setDays] = useState(null);
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [loading, setLoading] = useState(true);

  // Selected for bulk deletion
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [jobToDelete, setJobToDelete] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: '10',
        sort_by: sortBy,
        sort_order: sortOrder
      });
      if (search.trim()) params.append('search', search.trim());
      if (statusFilter !== 'all') params.append('status_filter', statusFilter);
      if (days) params.append('days', days.toString());

      const res = await api.listVerifications(params.toString());
      setItems(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error("History fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, statusFilter, days, sortBy, sortOrder]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchHistory();
  };

  const handleDeleteConfirm = async () => {
    try {
      if (jobToDelete) {
        await api.deleteVerification(jobToDelete);
        setJobToDelete(null);
      } else if (selectedIds.size > 0) {
        for (const id of selectedIds) {
          await api.deleteVerification(id);
        }
        setSelectedIds(new Set());
      }
      setShowDeleteModal(false);
      fetchHistory();
    } catch (err) {
      alert("Failed to delete record: " + err.message);
    }
  };

  const handleToggleSave = async (id, currentlySaved) => {
    try {
      if (currentlySaved) {
        await api.removeSaved(id);
      } else {
        await api.saveVerification(id);
      }
      fetchHistory();
    } catch (err) {
      console.error("Save error:", err);
    }
  };

  const toggleSelect = (id) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === items.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(items.map((i) => i.id)));
    }
  };

  const getReliabilityColor = (score) => {
    if (score >= 0.7) return '#16A34A';
    if (score >= 0.4) return '#EA580C';
    return '#DC2626';
  };

  return (
    <div style={{ flex: 1, backgroundColor: '#FAF8F5', padding: '36px 40px', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#78716C', fontFamily: 'var(--font-mono)' }}>
              VERIFICATION AUDIT LOGS
            </div>
            <h1 className="font-serif" style={{ fontSize: '2.5rem', fontWeight: 600, color: '#1C1917', lineHeight: 1.15, marginTop: '4px' }}>
              Verification History
            </h1>
            <p style={{ fontSize: '0.86rem', color: '#57534E', marginTop: '4px' }}>
              Search, filter, export, and manage your private past claim verification records.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            {selectedIds.size > 0 && (
              <button
                onClick={() => {
                  setJobToDelete(null);
                  setShowDeleteModal(true);
                }}
                style={{
                  backgroundColor: '#DC2626',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '8px 14px',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <Trash2 size={14} />
                Delete Selected ({selectedIds.size})
              </button>
            )}

            <button
              onClick={onNewVerification}
              style={{
                backgroundColor: '#1C1917',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '6px',
                padding: '8px 16px',
                fontSize: '0.84rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              + New Verification
            </button>
          </div>
        </div>

        {/* Filter & Search Bar */}
        <div
          style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #E8E5DC',
            borderRadius: '10px',
            padding: '16px 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '14px'
          }}
        >
          {/* Search Input */}
          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: '280px' }}>
            <Search size={16} color="#78716C" />
            <input
              type="text"
              placeholder="Search by title or text..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                border: 'none',
                outline: 'none',
                fontSize: '0.84rem',
                color: '#1C1917',
                width: '100%'
              }}
            />
          </form>

          {/* Sorter & Filters */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <select
              value={days || ''}
              onChange={(e) => setDays(e.target.value ? parseInt(e.target.value) : null)}
              style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid #D5D1C6', backgroundColor: '#FAF8F5', fontSize: '0.78rem' }}
            >
              <option value="">All Time</option>
              <option value="7">Last 7 Days</option>
              <option value="30">Last 30 Days</option>
              <option value="90">Last 90 Days</option>
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid #D5D1C6', backgroundColor: '#FAF8F5', fontSize: '0.78rem' }}
            >
              <option value="created_at">Sort by Date</option>
              <option value="reliability_score">Sort by Reliability</option>
              <option value="total_claims">Sort by Total Claims</option>
            </select>

            <button
              onClick={() => setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')}
              style={{ backgroundColor: '#FAF8F5', border: '1px solid #D5D1C6', borderRadius: '6px', padding: '6px 10px', fontSize: '0.78rem', cursor: 'pointer' }}
            >
              {sortOrder === 'desc' ? '↓ Desc' : '↑ Asc'}
            </button>
          </div>
        </div>

        {/* Table Card */}
        <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '16px', overflowX: 'auto' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '48px', color: '#78716C', fontSize: '0.86rem' }}>
              <RefreshCw size={18} className="pulse-indicator" style={{ margin: '0 auto 8px auto' }} />
              Loading history...
            </div>
          ) : items.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '60px 20px' }}>
              <History size={40} color="#D5D1C6" style={{ margin: '0 auto 12px auto' }} />
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#1C1917', marginBottom: '4px' }}>
                No Records Found
              </h3>
              <p style={{ fontSize: '0.82rem', color: '#78716C', maxWidth: '360px', margin: '0 auto 18px auto' }}>
                {search ? `No verifications match "${search}". Try clearing your search.` : 'You have not submitted any verifications yet.'}
              </p>
              <button
                onClick={onNewVerification}
                style={{ backgroundColor: '#1C1917', color: '#FFFFFF', border: 'none', borderRadius: '6px', padding: '8px 16px', fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer' }}
              >
                Start Verification
              </button>
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #E8E5DC', color: '#78716C' }}>
                  <th style={{ padding: '10px 8px', width: '30px' }}>
                    <input
                      type="checkbox"
                      checked={selectedIds.size === items.length && items.length > 0}
                      onChange={toggleSelectAll}
                    />
                  </th>
                  <th style={{ padding: '10px 8px' }}>Title & Text Preview</th>
                  <th style={{ padding: '10px 8px' }}>Date</th>
                  <th style={{ padding: '10px 8px' }}>Claims (S / C / NEI)</th>
                  <th style={{ padding: '10px 8px' }}>Reliability R(a)</th>
                  <th style={{ padding: '10px 8px' }}>Status</th>
                  <th style={{ padding: '10px 8px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((job) => {
                  const isChecked = selectedIds.has(job.id);
                  return (
                    <tr
                      key={job.id}
                      style={{ borderBottom: '1px solid #F3EFE7', color: '#1C1917', cursor: 'pointer' }}
                      onClick={() => onViewVerification(job.id)}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#FAF8F5')}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      <td style={{ padding: '12px 8px' }} onClick={(e) => e.stopPropagation()}>
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => toggleSelect(job.id)}
                        />
                      </td>

                      <td style={{ padding: '12px 8px', maxWidth: '340px' }}>
                        <div style={{ fontWeight: 600, color: '#1C1917', marginBottom: '2px' }}>{job.title}</div>
                        <div style={{ color: '#78716C', fontSize: '0.74rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {job.original_text}
                        </div>
                      </td>

                      <td style={{ padding: '12px 8px', color: '#78716C', whiteSpace: 'nowrap' }}>
                        {new Date(job.created_at).toLocaleDateString()}
                      </td>

                      <td style={{ padding: '12px 8px', whiteSpace: 'nowrap' }}>
                        <span style={{ color: '#16A34A', fontWeight: 600 }}>{job.supported_count}</span> /{' '}
                        <span style={{ color: '#DC2626', fontWeight: 600 }}>{job.contradicted_count}</span> /{' '}
                        <span style={{ color: '#CA8A04', fontWeight: 600 }}>{job.nei_count}</span>
                      </td>

                      <td style={{ padding: '12px 8px', fontWeight: 700, color: getReliabilityColor(job.reliability_score) }}>
                        {(job.reliability_score * 100).toFixed(0)}%
                      </td>

                      <td style={{ padding: '12px 8px' }}>
                        <span style={{
                          backgroundColor: '#DCFCE7',
                          color: '#15803D',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontSize: '0.72rem',
                          fontWeight: 600
                        }}>
                          {job.processing_status}
                        </span>
                      </td>

                      <td style={{ padding: '12px 8px', textAlign: 'right', whiteSpace: 'nowrap' }} onClick={(e) => e.stopPropagation()}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '6px' }}>
                          {/* Bookmark */}
                          <button
                            onClick={() => handleToggleSave(job.id, job.is_saved)}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', color: job.is_saved ? '#16A34A' : '#78716C', padding: '4px' }}
                            title={job.is_saved ? 'Remove Bookmark' : 'Save to Bookmarks'}
                          >
                            {job.is_saved ? <BookmarkCheck size={14} color="#16A34A" /> : <Bookmark size={14} />}
                          </button>

                          {/* PDF download */}
                          <a
                            href={api.downloadPdfUrl(job.id)}
                            target="_blank"
                            rel="noreferrer"
                            style={{ color: '#57534E', padding: '4px', display: 'flex', alignItems: 'center' }}
                            title="Download PDF Report"
                          >
                            <FileText size={14} />
                          </a>

                          {/* Delete */}
                          <button
                            onClick={() => {
                              setJobToDelete(job.id);
                              setShowDeleteModal(true);
                            }}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#DC2626', padding: '4px' }}
                            title="Delete Record"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}

          {/* Pagination */}
          {total > 10 && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #E8E5DC', fontSize: '0.78rem', color: '#78716C' }}>
              <span>Showing {items.length} of {total} verifications</span>
              <div style={{ display: 'flex', gap: '6px' }}>
                <button
                  disabled={page === 1}
                  onClick={() => setPage(page - 1)}
                  style={{ padding: '4px 10px', borderRadius: '4px', border: '1px solid #D5D1C6', backgroundColor: '#FAF8F5', cursor: page === 1 ? 'not-allowed' : 'pointer' }}
                >
                  Previous
                </button>
                <button
                  disabled={page * 10 >= total}
                  onClick={() => setPage(page + 1)}
                  style={{ padding: '4px 10px', borderRadius: '4px', border: '1px solid #D5D1C6', backgroundColor: '#FAF8F5', cursor: page * 10 >= total ? 'not-allowed' : 'pointer' }}
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Delete Confirmation Modal (Section 9) */}
        {showDeleteModal && (
          <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(28,25,23,0.4)', backdropFilter: 'blur(3px)', zIndex: 60, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ width: '420px', backgroundColor: '#FFFFFF', borderRadius: '12px', padding: '24px', border: '1px solid #E8E5DC', boxShadow: '0 20px 40px rgba(0,0,0,0.15)' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#1C1917', marginBottom: '8px' }}>
                Confirm Deletion
              </h3>
              <p style={{ fontSize: '0.84rem', color: '#57534E', lineHeight: '1.5', marginBottom: '20px' }}>
                {jobToDelete
                  ? 'Are you sure you want to permanently delete this verification and all associated atomic claim records? This cannot be undone.'
                  : `Are you sure you want to delete ${selectedIds.size} selected verification analyses?`}
              </p>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button
                  onClick={() => setShowDeleteModal(false)}
                  style={{ backgroundColor: '#FAF8F5', border: '1px solid #D5D1C6', borderRadius: '6px', padding: '7px 14px', fontSize: '0.8rem', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteConfirm}
                  style={{ backgroundColor: '#DC2626', color: '#FFFFFF', border: 'none', borderRadius: '6px', padding: '7px 16px', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer' }}
                >
                  Yes, Delete Permanently
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
