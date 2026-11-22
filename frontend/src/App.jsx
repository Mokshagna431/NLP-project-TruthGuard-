import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import LandingPage from './components/LandingPage';
import AboutPage from './components/AboutPage';
import DocsPage from './components/DocsPage';
import ContactPage from './components/ContactPage';
import AuthModal from './components/AuthModal';
import Sidebar from './components/Sidebar';
import DashboardOverview from './components/DashboardOverview';
import FactcheckView from './components/FactcheckView';
import NewVerificationView from './components/NewVerificationView';
import VerificationResultsView from './components/VerificationResultsView';
import CitationVerificationView from './components/CitationVerificationView';
import BenchmarkDashboardView from './components/BenchmarkDashboardView';
import HistoryView from './components/HistoryView';
import SavedCasesView from './components/SavedCasesView';
import AnalyticsView from './components/AnalyticsView';
import EvidenceLibraryView from './components/EvidenceLibraryView';
import ProfileView from './components/ProfileView';
import SettingsView from './components/SettingsView';
import AdminDashboard from './components/AdminDashboard';
import CommandPalette from './components/CommandPalette';
import NotificationsModal from './components/NotificationsModal';
import { api, getUser, getToken } from './services/api';
import { PRESET_DOCUMENTS } from './data/mockData';

export default function App() {
  // Current user state
  const [currentUser, setCurrentUser] = useState(getUser());
  
  // View routing: 'landing', 'about', 'docs', 'contact', OR dashboard views:
  // 'overview', 'new-verification', 'results', 'history', 'saved', 'analytics', 'evidence', 'profile', 'settings', 'admin'
  const [currentView, setCurrentView] = useState('landing');
  
  // Selected job for results view
  const [currentJob, setCurrentJob] = useState(null);

  // Modals
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [isCommandOpen, setIsCommandOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);

  // Check user on initial load
  useEffect(() => {
    if (getToken()) {
      api.getMe()
        .then((user) => {
          setCurrentUser(user);
        })
        .catch(() => {
          api.logout();
          setCurrentUser(null);
        });
    }
  }, []);

  // Global key shortcut for Command Palette (⌘K / Ctrl+K)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsCommandOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleOpenAuth = (mode = 'login') => {
    setAuthMode(mode);
    setIsAuthOpen(true);
  };

  const handleAuthSuccess = (user) => {
    setCurrentUser(user);
    setCurrentView('overview');
  };

  const handleLogout = async () => {
    await api.logout();
    setCurrentUser(null);
    setCurrentView('landing');
  };

  const handleStartVerification = () => {
    if (currentUser) {
      setCurrentView('new-verification');
    } else {
      handleOpenAuth('register');
    }
  };

  const handleVerificationComplete = (job) => {
    setCurrentJob(job);
    setCurrentView('results');
  };

  const handleViewVerification = async (jobId) => {
    try {
      const job = await api.getVerification(jobId);
      setCurrentJob(job);
      setCurrentView('results');
    } catch (err) {
      console.error("Failed to load job:", err);
      // Fallback to sample if offline/mock
      const sample = PRESET_DOCUMENTS[0];
      setCurrentJob({
        id: sample.id,
        title: sample.title,
        original_text: sample.plainText,
        corrected_text: sample.correctedText,
        reliability_score: sample.credibilityScore / 100,
        mean_rho: 0.72,
        max_p_c: 0.96,
        total_claims: sample.claims.length,
        supported_count: sample.claimsSummary.accurate,
        contradicted_count: sample.claimsSummary.inaccurate,
        nei_count: sample.claimsSummary.subjective,
        corrections_count: 3,
        latency_sec: 1.45,
        created_at: new Date().toISOString(),
        verification_mode: 'standard',
        claims: sample.claims.map((c, idx) => ({
          id: c.id,
          claim_number: idx + 1,
          claim_text: c.claim,
          predicted_label: c.status.toUpperCase(),
          p_supported: c.probabilities.p_e,
          p_contradicted: c.probabilities.p_c,
          p_nei: c.probabilities.p_n,
          reliability: c.probabilities.p_e + 0.5 * c.probabilities.p_n,
          rationale: c.justification,
          best_evidence: c.justification,
          evidence_items: [{ source_title: c.sourceTitle, source_url: c.source }],
          corrections: c.suggestedRevision ? [{ suggested_correction: c.suggestedRevision }] : []
        }))
      });
      setCurrentView('results');
    }
  };

  const handleRerun = async (jobId) => {
    try {
      const newJob = await api.rerunVerification(jobId);
      setCurrentJob(newJob);
      setCurrentView('results');
    } catch (err) {
      alert("Re-run failed: " + err.message);
    }
  };

  const isPublicPage = ['landing', 'about', 'docs', 'contact'].includes(currentView);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: '#FAF8F5' }}>
      
      {/* If Public Page: Render Top Public Navbar */}
      {isPublicPage ? (
        <>
          <Navbar
            currentView={currentView}
            setCurrentView={setCurrentView}
            currentUser={currentUser}
            onOpenAuth={handleOpenAuth}
            onLogout={handleLogout}
          />

          <main style={{ flex: 1 }}>
            {currentView === 'landing' && (
              <LandingPage
                onStartVerification={handleStartVerification}
                onOpenAuth={handleOpenAuth}
                currentUser={currentUser}
              />
            )}
            {currentView === 'about' && (
              <AboutPage onStartVerification={handleStartVerification} />
            )}
            {currentView === 'docs' && (
              <DocsPage />
            )}
            {currentView === 'contact' && (
              <ContactPage currentUser={currentUser} />
            )}
          </main>
        </>
      ) : (
        /* Authenticated Proof Desk Dashboard Workspace */
        <div style={{ display: 'flex', minHeight: '100vh' }}>
          <Sidebar
            activeNav={currentView}
            setActiveNav={(nav) => {
              if (nav === 'dashboard') setCurrentView('overview');
              else setCurrentView(nav);
            }}
            currentUser={currentUser}
            notificationsCount={1}
            onOpenNotifications={() => setIsNotificationsOpen(true)}
            onLogout={handleLogout}
          />

          <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, overflowX: 'hidden' }}>
            {currentView === 'overview' && (
              <DashboardOverview
                currentUser={currentUser}
                onNewVerification={() => setCurrentView('new-verification')}
                onViewVerification={handleViewVerification}
              />
            )}

            {currentView === 'factcheck' && (
              <FactcheckView
                onNewFactcheck={() => {}}
                onOpenSettings={() => setCurrentView('settings')}
                onOpenApi={() => setCurrentView('docs')}
                onViewJob={(job) => {
                  setCurrentJob(job);
                  setCurrentView('results');
                }}
              />
            )}

            {currentView === 'citation' && (
              <CitationVerificationView />
            )}

            {currentView === 'benchmarks' && (
              <BenchmarkDashboardView />
            )}

            {currentView === 'new-verification' && (
              <NewVerificationView
                onVerificationComplete={handleVerificationComplete}
                onOpenDocs={() => setCurrentView('docs')}
              />
            )}

            {currentView === 'results' && (
              <VerificationResultsView
                job={currentJob}
                onRerun={handleRerun}
                onBackToDashboard={() => setCurrentView('overview')}
              />
            )}

            {currentView === 'history' && (
              <HistoryView
                onViewVerification={handleViewVerification}
                onNewVerification={() => setCurrentView('new-verification')}
              />
            )}

            {currentView === 'saved' && (
              <SavedCasesView
                onViewVerification={handleViewVerification}
                onNewVerification={() => setCurrentView('new-verification')}
              />
            )}

            {currentView === 'analytics' && (
              <AnalyticsView
                onNewVerification={() => setCurrentView('new-verification')}
                onOpenSearch={() => setIsCommandOpen(true)}
              />
            )}

            {currentView === 'evidence' && (
              <EvidenceLibraryView />
            )}

            {currentView === 'profile' && (
              <ProfileView
                currentUser={currentUser}
                onUpdateUser={setCurrentUser}
                onLogout={handleLogout}
              />
            )}

            {currentView === 'settings' && (
              <SettingsView onLogout={handleLogout} />
            )}

            {currentView === 'admin' && (
              <AdminDashboard />
            )}

            {currentView === 'help' && (
              <DocsPage />
            )}
          </main>
        </div>
      )}

      {/* Global Modals */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        initialMode={authMode}
        onAuthSuccess={handleAuthSuccess}
      />

      <CommandPalette
        isOpen={isCommandOpen}
        onClose={() => setIsCommandOpen(false)}
        onSelectAction={(action) => {
          if (action.nav) setCurrentView(action.nav);
        }}
      />

      <NotificationsModal
        isOpen={isNotificationsOpen}
        onClose={() => setIsNotificationsOpen(false)}
      />
    </div>
  );
}
