import React from "react"
import { Modal } from "antd"

const RequestUser: React.FC = () => {
    const [username, setUsername] = React.useState('')
    const [focused, setFocused] = React.useState(false)
    const [isNarrow, setIsNarrow] = React.useState<boolean>(typeof window !== 'undefined' ? window.innerWidth <= 1220 : false)
    const [showInfoModal, setShowInfoModal] = React.useState(false)

    React.useEffect(() => {
        const onResize = () => setIsNarrow(window.innerWidth <= 1220)
        window.addEventListener('resize', onResize)
        return () => window.removeEventListener('resize', onResize)
    }, [])

    const isValid = /^[a-zA-Z0-9-]{1,39}$/.test(username)

    // Reusable info content (used in aside and modal)
    const infoBody = (
        <>
            <p style={styles.infoIntro}>
                A quick overview of how we traverse GitHub Sponsors relationships.
            </p>
            <ul style={styles.infoList}>
                <li>
                    <strong>1.</strong> You enqueue a username; we create a crawl job.
                </li>
                <li>
                    <strong>2.</strong> A background worker queries sponsors and sponsoring via the GitHub API.
                </li>
                <li>
                    <strong>3.</strong> We paginate breadth‑first, de‑duplicate nodes, and respect rate limits with backoff.
                </li>
                <li>
                    <strong>4.</strong> Each edge is stored with direction (sponsors vs. sponsoring) and timestamps.
                </li>
                <li>
                    <strong>5.</strong> Subsequent visits hydrate this graph as new results arrive.
                </li>
            </ul>
            <p style={styles.infoFootnote}>
                We avoid storing sensitive data and cache responses briefly to reduce API load.
            </p>
        </>
    )

    return (
        <>
            <section
                className="h-full w-full flex flex-1 gap-10 pl-2"
            >
                {/* New two-column layout: left = existing UI, right = info panel */}
                <div className="flex w-full flex-wrap gap-6 items-start">
                    <div className="w-full h-full flex flex-col gap-6 min-w-0 flex-1 min-[1200px]:min-w-[700px]">

                        {/* TODO: Make this an Antd form element */}
                        <div className="w-full flex-1 h-full min-w-0">
                            <div style={styles.card} className="flex flex-col flex-1 h-full jus">
                                <header style={styles.header}>
                                    <div style={styles.headerRow}>
                                        <h1 style={styles.title}>Request GitHub User</h1>
                                        {isNarrow && (
                                            <button
                                                type="button"
                                                aria-label="How the scraper works"
                                                onClick={() => setShowInfoModal(true)}
                                                style={styles.infoButton}
                                            >
                                                ?
                                            </button>
                                        )}
                                    </div>
                                    <p style={styles.subtitle}>
                                        Enqueue a username to discover sponsor relationships. We’ll handle the processing in the background.
                                    </p>
                                </header>

                                <form
                                    style={styles.form}
                                    className=""
                                    onSubmit={(e) => {
                                        e.preventDefault()
                                        // Intentionally left unimplemented (design only)
                                    }}
                                >
                                    <label htmlFor="github-username" style={styles.label}>
                                        GitHub username
                                    </label>

                                    <div
                                        style={{
                                            ...styles.inputWrap,
                                            boxShadow: focused
                                                ? '0 0 0 6px rgba(59,130,246,0.12)'
                                                : '0 1px 0 0 var(--hairline, rgba(148,163,184,0.18))',
                                            borderColor: focused ? 'var(--accent, #3b82f6)' : 'var(--line, rgba(148,163,184,0.25))',
                                        }}
                                    >
                                        <span aria-hidden="true" style={styles.inputIcon}>
                                            @
                                        </span>
                                        <input
                                            id="github-username"
                                            name="github-username"
                                            placeholder="octocat"
                                            value={username}
                                            onChange={(e) => setUsername(e.target.value.trim())}
                                            onFocus={() => setFocused(true)}
                                            onBlur={() => setFocused(false)}
                                            pattern="^[a-zA-Z0-9-]{1,39}$"
                                            title="1–39 characters: letters, numbers, or hyphens"
                                            autoComplete="off"
                                            spellCheck={false}
                                            style={styles.input}
                                        />
                                    </div>

                                    <button
                                        type="submit"
                                        disabled={!isValid}
                                        style={{
                                            ...styles.button,
                                            opacity: isValid ? 1 : 0.6,
                                            cursor: isValid ? 'pointer' : 'not-allowed',
                                        }}
                                    >
                                        <span>Enqueue</span>
                                        <svg
                                            width="16"
                                            height="16"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            style={{ marginLeft: 8 }}
                                            aria-hidden="true"
                                        >
                                            <path d="M5 12h14M13 5l7 7-7 7" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                                        </svg>
                                    </button>

                                    <p style={styles.helpText}>
                                        We’ll queue the request and populate sponsor links as they’re discovered. You can close this page safely.
                                    </p>
                                </form>
                            </div>
                        </div>
                        <div className="flex flex-row items-center justify-center text-center text-sm">
                            <div className="flex items-center gap-3">
                                <svg width="16" height="16" viewBox="0 0 16 26" fill="none" aria-hidden="true">
                                    <path d="M12 19V5m0 0l-6 6m6-6 6 6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                                <span>Enter a Username - Our Crawler Builds This Graph</span>
                            </div>
                        </div>


                        {/* Moved: existing visualization block */}
                        <div style={{ width: '100%', display: 'flex', justifyContent: 'center' }}>
                            <div
                                // Constrain to column width
                                style={{ width: '100%', position: 'relative' }}
                                ref={(el) => {
                                    if (!el) return
                                    if ((el as any)._animated) return
                                        ; (el as any)._animated = true

                                    const run = async () => {
                                        const { gsap } = await import('gsap')
                                        const ease = 'cubic-bezier(0.22, 1, 0.36, 1)'

                                        const $all = (sel: string) => Array.from(el.querySelectorAll(sel))

                                        const prepPaths = (paths: Element[]) => {
                                            paths.forEach((p) => {
                                                const path = p as SVGPathElement
                                                const len = path.getTotalLength()
                                                gsap.set(path, { strokeDasharray: len, strokeDashoffset: len })
                                            })
                                        }

                                        const nodes = $all('.node')
                                        const rootNode = $all('.node-root')
                                        const l2Nodes = $all('.node-l2')
                                        const l3Left = $all('.node-l3-left')
                                        const l3Right = $all('.node-l3-right')

                                        const rootConns = $all('.connector-root')
                                        const leftConns = $all('.connector-left')
                                        const rightConns = $all('.connector-right')

                                        gsap.set(nodes, { opacity: 0, y: -20 })
                                        prepPaths([...rootConns, ...leftConns, ...rightConns])

                                        const tl = gsap.timeline({ defaults: { ease } })

                                        tl.to(rootNode, { opacity: 1, y: 0, duration: 0.5 })
                                            .to(rootConns, { strokeDashoffset: 0, duration: 0.7, stagger: 0.08 }, '-=0.1')
                                            .to(l2Nodes, { opacity: 1, y: 0, duration: 0.5, stagger: 0.1 })
                                            .to(leftConns, { strokeDashoffset: 0, duration: 0.7, stagger: 0.06 }, '-=0.1')
                                            .to(rightConns, { strokeDashoffset: 0, duration: 0.7, stagger: 0.06 }, '-=0.55')
                                            .to(l3Left, { opacity: 1, y: 0, duration: 0.45, stagger: 0.06 }, '-=0.2')
                                            .to(l3Right, { opacity: 1, y: 0, duration: 0.45, stagger: 0.06 }, '-=0.35')
                                    }

                                    void run()
                                }}
                            >
                                {/* Arrow hint pointing up toward the form */}

                                {/* Visualization: 3-tier binary tree */}
                                <div
                                    aria-hidden="true"
                                    style={{
                                        border: '1px solid var(--line, rgba(148,163,184,0.18))',
                                        borderRadius: 16,
                                        padding: 16,
                                        background: 'color-mix(in srgb, #141414 62%, transparent)',
                                        boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.03), 0 10px 40px rgba(0,0,0,0.35)',
                                        backdropFilter: 'saturate(120%) blur(6px)',
                                    }}
                                >
                                    <svg viewBox="0 0 920 340" width="100%" style={{ display: 'block', height: 'auto' }} preserveAspectRatio="xMidYMid meet">
                                        <defs>
                                            <linearGradient id="nodeFill" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="0%" stopColor="rgba(30,41,59,0.65)" />
                                                <stop offset="100%" stopColor="rgba(15,23,42,0.55)" />
                                            </linearGradient>
                                            <linearGradient id="accentFill" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="0%" stopColor="color-mix(in srgb, var(--accent, #3b82f6) 22%, transparent)" />
                                                <stop offset="100%" stopColor="transparent" />
                                            </linearGradient>
                                            <filter id="shadow" x="-20%" y="-20%" width="200%" height="200%">
                                                <feDropShadow dx="0" dy="10" stdDeviation="14" floodColor="#000000" floodOpacity="0.35" />
                                            </filter>
                                        </defs>

                                        {/* Scale the whole tree around the SVG center to occupy more space while staying centered */}
                                        <g transform="translate(460 190) scale(1.00) translate(-460 -170)">
                                            {/* Connectors: primary from root */}
                                            <path className="connector-root" d="M460 74 C460 100 260 96 260 120" stroke="var(--accent, #3b82f6)" strokeWidth="1.8" fill="none" opacity="0.75" />
                                            <path className="connector-root" d="M460 74 C460 100 660 96 660 120" stroke="var(--accent, #3b82f6)" strokeWidth="1.8" fill="none" opacity="0.75" />

                                            {/* Connectors: sponsors side */}
                                            <path className="connector-left" d="M260 164 C260 190 140 190 140 218" stroke="rgba(148,163,184,0.35)" strokeWidth="1.3" fill="none" />
                                            <path className="connector-left" d="M260 164 C260 190 260 190 260 218" stroke="rgba(148,163,184,0.35)" strokeWidth="1.3" fill="none" />
                                            <path className="connector-left" d="M260 164 C260 190 380 190 380 218" stroke="rgba(148,163,184,0.35)" strokeWidth="1.3" fill="none" />

                                            {/* Connectors: sponsoring side */}
                                            <path className="connector-right" d="M660 164 C660 190 540 190 540 218" stroke="rgba(148,163,184,0.35)" strokeWidth="1.3" fill="none" />
                                            <path className="connector-right" d="M660 164 C660 190 660 190 660 218" stroke="rgba(148,163,184,0.35)" strokeWidth="1.3" fill="none" />
                                            <path className="connector-right" d="M660 164 C660 190 780 190 780 218" stroke="rgba(148,163,184,0.35)" strokeWidth="1.3" fill="none" />

                                            {/* Root node: User */}
                                            <g className="node node-root" filter="url(#shadow)">
                                                <rect x="400" y="30" width="120" height="44" rx="12" fill="url(#nodeFill)" stroke="color-mix(in srgb, var(--accent, #3b82f6) 55%, transparent)" />
                                                {/* <rect x="400" y="30" width="10" height="44" rx="12" fill="url(#accentFill)" opacity="0.35" /> */}
                                                <text x="460" y="57" textAnchor="middle" fontSize="14" fontWeight="600" fill="var(--text-strong, #e5e7eb)">
                                                    User
                                                </text>
                                            </g>

                                            {/* Level 2: Sponsors and Sponsoring */}
                                            <g className="node node-l2" filter="url(#shadow)">
                                                <rect x="200" y="120" width="120" height="44" rx="12" fill="url(#nodeFill)" stroke="rgba(148,163,184,0.25)" />
                                                <text x="260" y="147" textAnchor="middle" fontSize="13" fontWeight="600" fill="var(--text, #cbd5e1)">
                                                    Sponsors
                                                </text>
                                            </g>
                                            <g className="node node-l2" filter="url(#shadow)">
                                                <rect x="600" y="120" width="120" height="44" rx="12" fill="url(#nodeFill)" stroke="rgba(148,163,184,0.25)" />
                                                <text x="660" y="147" textAnchor="middle" fontSize="13" fontWeight="600" fill="var(--text, #cbd5e1)">
                                                    Sponsoring
                                                </text>
                                            </g>

                                            {/* Level 3 leaves: Sponsors side */}
                                            <g className="node node-l3 node-l3-left" filter="url(#shadow)">
                                                <rect x="95" y="218" width="90" height="40" rx="10" fill="url(#nodeFill)" stroke="rgba(148,163,184,0.18)" />
                                                <text x="140" y="243" textAnchor="middle" fontSize="12.5" fill="#cbd5e1">@alice</text>
                                            </g>
                                            <g className="node node-l3 node-l3-left" filter="url(#shadow)">
                                                <rect x="215" y="218" width="90" height="40" rx="10" fill="url(#nodeFill)" stroke="rgba(148,163,184,0.18)" />
                                                <text x="260" y="243" textAnchor="middle" fontSize="12.5" fill="#cbd5e1">@bob</text>
                                            </g>
                                            <g className="node node-l3 node-l3-left" filter="url(#shadow)">
                                                <rect x="335" y="218" width="90" height="40" rx="10" fill="url(#nodeFill)" stroke="rgba(148,163,184,0.18)" />
                                                <text x="380" y="243" textAnchor="middle" fontSize="12.5" fill="#cbd5e1">@carol</text>
                                            </g>

                                            {/* Level 3 leaves: Sponsoring side */}
                                            <g className="node node-l3 node-l3-right" filter="url(#shadow)">
                                                <rect x="495" y="218" width="90" height="40" rx="10" fill="url(#nodeFill)" stroke="rgba(148,163,184,0.18)" />
                                                <text x="540" y="243" textAnchor="middle" fontSize="12.5" fill="#cbd5e1">@neo</text>
                                            </g>
                                            <g className="node node-l3 node-l3-right" filter="url(#shadow)">
                                                <rect x="615" y="218" width="90" height="40" rx="10" fill="url(#nodeFill)" stroke="rgba(148,163,184,0.18)" />
                                                <text x="660" y="243" textAnchor="middle" fontSize="12.5" fill="#cbd5e1">@trinity</text>
                                            </g>
                                            <g className="node node-l3 node-l3-right" filter="url(#shadow)">
                                                <rect x="735" y="218" width="90" height="40" rx="10" fill="url(#nodeFill)" stroke="rgba(148,163,184,0.18)" />
                                                <text x="780" y="243" textAnchor="middle" fontSize="12.5" fill="#cbd5e1">@morpheus</text>
                                            </g>

                                            {/* Legend */}
                                            <g>
                                                <rect x="18" y="16" width="150" height="28" rx="8" fill="rgba(2,6,23,0.4)" stroke="rgba(148,163,184,0.18)" />
                                                <circle cx="34" cy="30" r="4" fill="var(--accent, #3b82f6)" />
                                                <text x="48" y="34" fontSize="12" fill="var(--muted, #94a3b8)">Crawler traversal</text>
                                            </g>
                                        </g>
                                    </svg>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Right column (new info panel) */}
                    {!isNarrow && (
                        <aside className="min-w-0 max-w-[575px] h-full flex-1">
                            <div style={styles.infoCard} className="h-full flex-1">
                                <h2 style={styles.infoTitle} className="text-[24px]">How the scraper works</h2>
                                {infoBody}
                            </div>
                        </aside>
                    )}
                </div>

                {/* Modal shown on narrow screens */}
                {isNarrow && (
                    <Modal
                        open={showInfoModal}
                        title="How the scraper works"
                        onCancel={() => setShowInfoModal(false)}
                        footer={null}
                        centered
                        width={560}
                    >
                        {infoBody}
                    </Modal>
                )}
            </section>
        </>
    )
}

const styles: Record<string, React.CSSProperties> = {
    // Responsive, non-overflowing layout
    infoCard: {
        background: 'color-mix(in srgb, #141414 62%, transparent)',
        border: '1px solid var(--line, rgba(148,163,184,0.2))',
        borderRadius: 16,
        padding: '28px',
        boxShadow: '0 20px 70px rgba(0,0,0,0.30)',
        backdropFilter: 'saturate(120%) blur(6px)',
    },
    infoTitle: {
        margin: 0,
        fontWeight: 600,
        letterSpacing: '-0.01em',
        color: 'var(--text-strong, #f1f5f9)',
    },
    infoIntro: {
        margin: '8px 0 10px',
        color: 'var(--muted, #94a3b8)',
        lineHeight: 1.5,
        fontSize: 13.5,
    },
    infoList: {
        margin: '8px 0 8px',
        paddingLeft: 0,
        listStyleType: 'none',
        display: 'grid',
        gap: 8,
        color: 'var(--text, #cbd5e1)',
        fontSize: 13.5,
    },
    infoFootnote: {
        marginTop: 10,
        color: 'var(--muted, #94a3b8)',
        fontSize: 12,
    },

    card: {
        // Subtle elevated card over #141414
        background: 'color-mix(in srgb, #141414 68%, transparent)',
        border: '1px solid var(--line, rgba(148,163,184,0.2))',
        borderRadius: 16,
        padding: '28px clamp(20px, 4vw, 32px)',
        boxShadow: '0 20px 70px rgba(0,0,0,0.35)',
        backdropFilter: 'saturate(120%) blur(8px)',
    },
    header: {
        marginBottom: 20,
    },
    // New: header row to place title and ? button on opposite sides
    headerRow: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 12,
    },
    // New: compact question button
    infoButton: {
        width: 32,
        height: 32,
        borderRadius: 999,
        border: '1px solid var(--line, rgba(148,163,184,0.25))',
        background: 'transparent',
        color: 'var(--muted, #94a3b8)',
        cursor: 'pointer',
        fontWeight: 700,
        lineHeight: 1,
    },
    title: {
        margin: 0,
        fontSize: 'clamp(20px, 3vw, 24px)',
        fontWeight: 600,
        letterSpacing: '-0.01em',
        color: 'var(--text-strong, #f1f5f9)',
    },
    subtitle: {
        margin: '8px 0 0',
        color: 'var(--muted, #94a3b8)',
        lineHeight: 1.5,
        fontSize: 14,
    },
    form: {
        display: 'grid',
        gap: 14,
        marginTop: 8,
    },
    label: {
        fontSize: 12,
        letterSpacing: '0.04em',
        textTransform: 'uppercase',
        color: 'var(--muted-2, #9aa7b4)',
    },
    inputWrap: {
        position: 'relative',
        border: '1px solid',
        borderRadius: 12,
        background: 'var(--input-bg, rgba(20,20,20,0.7))',
        transition: 'box-shadow 160ms ease, border-color 160ms ease',
    },
    inputIcon: {
        position: 'absolute',
        left: 12,
        top: '50%',
        transform: 'translateY(-50%)',
        color: 'var(--muted, #94a3b8)',
        fontSize: 14,
    },
    input: {
        width: '100%',
        height: 46,
        background: 'transparent',
        border: 'none',
        outline: 'none',
        color: 'var(--text, #e5e7eb)',
        padding: '0 14px 0 32px',
        fontSize: 14,
        letterSpacing: '0.2px',
        WebkitAppearance: 'none',
        boxSizing: 'border-box',
    },
    button: {
        height: 44,
        borderRadius: 12,
        border: '1px solid color-mix(in srgb, var(--accent, #3b82f6) 40%, transparent)',
        background:
            'linear-gradient(180deg, color-mix(in srgb, var(--accent, #3b82f6) 85%, #ffffff 0%), var(--accent, #3b82f6))',
        color: '#0b0f14',
        fontWeight: 600,
        fontSize: 14,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'transform 120ms ease, filter 120ms ease',
        outline: 'none',
        width: '100%',
        boxSizing: 'border-box',
    },
    helpText: {
        margin: '6px 2px 0',
        fontSize: 12,
        color: 'var(--muted, #94a3b8)',
    },
}

export default RequestUser