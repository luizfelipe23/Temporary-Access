import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'

type AuthMode = 'login' | 'register'

type User = {
  id: number
  name: string
  email: string
  active: boolean
}

type Credential = {
  id: number
  token: string
  created_at: string
  expires_at: string
  revoked: boolean
}

type TokenResponse = {
  access_token: string
  token_type: string
}

type ValidationResponse = {
  valid: boolean
  status: string
  expires_at?: string | null
  created_at?: string | null
}

const tokenStorageKey = 'temporary-access-token'

async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  token?: string,
): Promise<T> {
  const headers = new Headers(options.headers)

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(path, {
    ...options,
    headers,
  })

  if (!response.ok) {
    let detail = 'Nao foi possivel completar a requisicao.'

    try {
      const data = (await response.json()) as { detail?: string }
      detail = data.detail || detail
    } catch {
      detail = response.statusText || detail
    }

    throw new Error(detail)
  }

  return (await response.json()) as T
}

function formatDate(value: string | null | undefined) {
  if (!value) {
    return '-'
  }

  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

function App() {
  const [authMode, setAuthMode] = useState<AuthMode>('login')
  const [authName, setAuthName] = useState('')
  const [authEmail, setAuthEmail] = useState('')
  const [authPassword, setAuthPassword] = useState('')
  const [token, setToken] = useState(() => localStorage.getItem(tokenStorageKey) ?? '')
  const [user, setUser] = useState<User | null>(null)
  const [credentials, setCredentials] = useState<Credential[]>([])
  const [expiresInMinutes, setExpiresInMinutes] = useState(10)
  const [validationToken, setValidationToken] = useState('')
  const [validationResult, setValidationResult] = useState<ValidationResponse | null>(null)
  const [message, setMessage] = useState('')
  const [isBusy, setIsBusy] = useState(false)

  const activeCredentials = useMemo(
    () => credentials.filter((credential) => !credential.revoked).length,
    [credentials],
  )

  async function loadSession(currentToken: string) {
    const [currentUser, credentialList] = await Promise.all([
      apiRequest<User>('/api/auth/me', {}, currentToken),
      apiRequest<Credential[]>('/api/credentials', {}, currentToken),
    ])

    setUser(currentUser)
    setCredentials(credentialList)
  }

  useEffect(() => {
    if (!token) {
      return
    }

    loadSession(token).catch((error: unknown) => {
      localStorage.removeItem(tokenStorageKey)
      setToken('')
      setUser(null)
      setCredentials([])
      setMessage(error instanceof Error ? error.message : 'Sessao expirada.')
    })
  }, [token])

  async function handleAuthSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsBusy(true)
    setMessage('')

    try {
      if (authMode === 'register') {
        await apiRequest<User>('/api/auth/register', {
          method: 'POST',
          body: JSON.stringify({
            name: authName,
            email: authEmail,
            password: authPassword,
          }),
        })
      }

      const login = await apiRequest<TokenResponse>('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          email: authEmail,
          password: authPassword,
        }),
      })

      localStorage.setItem(tokenStorageKey, login.access_token)
      setToken(login.access_token)
      setAuthPassword('')
      setMessage(authMode === 'register' ? 'Conta criada e conectada.' : 'Login realizado.')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Erro inesperado.')
    } finally {
      setIsBusy(false)
    }
  }

  async function handleCreateCredential(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!token) {
      return
    }

    setIsBusy(true)
    setMessage('')

    try {
      const credential = await apiRequest<Credential>(
        '/api/credentials',
        {
          method: 'POST',
          body: JSON.stringify({
            expires_in_minutes: expiresInMinutes,
          }),
        },
        token,
      )

      setCredentials((currentCredentials) => [credential, ...currentCredentials])
      setValidationToken(credential.token)
      setMessage('Credencial criada.')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Erro ao criar credencial.')
    } finally {
      setIsBusy(false)
    }
  }

  async function handleValidateCredential(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsBusy(true)
    setMessage('')

    try {
      const result = await apiRequest<ValidationResponse>('/api/credentials/validate', {
        method: 'POST',
        body: JSON.stringify({
          token: validationToken,
        }),
      })

      setValidationResult(result)
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Erro ao validar credencial.')
    } finally {
      setIsBusy(false)
    }
  }

  async function handleRevokeCredential(credentialId: number) {
    if (!token) {
      return
    }

    setIsBusy(true)
    setMessage('')

    try {
      const revokedCredential = await apiRequest<Credential>(
        `/api/credentials/${credentialId}/revoke`,
        {
          method: 'POST',
        },
        token,
      )

      setCredentials((currentCredentials) =>
        currentCredentials.map((credential) =>
          credential.id === revokedCredential.id ? revokedCredential : credential,
        ),
      )
      setMessage('Credencial revogada.')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Erro ao revogar credencial.')
    } finally {
      setIsBusy(false)
    }
  }

  async function handleCopyToken(credentialToken: string) {
    await navigator.clipboard.writeText(credentialToken)
    setMessage('Token copiado.')
  }

  function handleLogout() {
    localStorage.removeItem(tokenStorageKey)
    setToken('')
    setUser(null)
    setCredentials([])
    setValidationResult(null)
    setMessage('Sessao encerrada.')
  }

  if (!user) {
    return (
      <main className="auth-shell">
        <section className="auth-panel">
          <div className="brand-block">
            <span className="brand-mark">TA</span>
            <div>
              <p className="eyebrow">Temporary Access</p>
              <h1>Acesso temporario</h1>
            </div>
          </div>

          <div className="mode-switch" aria-label="Modo de autenticacao">
            <button
              className={authMode === 'login' ? 'active' : ''}
              type="button"
              onClick={() => setAuthMode('login')}
            >
              Entrar
            </button>
            <button
              className={authMode === 'register' ? 'active' : ''}
              type="button"
              onClick={() => setAuthMode('register')}
            >
              Criar conta
            </button>
          </div>

          <form className="stack-form" onSubmit={handleAuthSubmit}>
            {authMode === 'register' && (
              <label>
                Nome
                <input
                  autoComplete="name"
                  minLength={2}
                  maxLength={100}
                  onChange={(event) => setAuthName(event.target.value)}
                  required
                  type="text"
                  value={authName}
                />
              </label>
            )}

            <label>
              Email
              <input
                autoComplete="email"
                onChange={(event) => setAuthEmail(event.target.value)}
                required
                type="email"
                value={authEmail}
              />
            </label>

            <label>
              Senha
              <input
                autoComplete={authMode === 'login' ? 'current-password' : 'new-password'}
                minLength={6}
                maxLength={128}
                onChange={(event) => setAuthPassword(event.target.value)}
                required
                type="password"
                value={authPassword}
              />
            </label>

            <button className="primary-action" disabled={isBusy} type="submit">
              {authMode === 'login' ? 'Entrar' : 'Criar e entrar'}
            </button>
          </form>

          {message && <p className="notice">{message}</p>}
        </section>
      </main>
    )
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-block compact">
          <span className="brand-mark">TA</span>
          <div>
            <p className="eyebrow">Temporary Access</p>
            <h1>Credenciais</h1>
          </div>
        </div>

        <div className="user-chip">
          <span>{user.name}</span>
          <button type="button" onClick={handleLogout}>
            Sair
          </button>
        </div>
      </header>

      <section className="metrics-row">
        <article>
          <span>Total</span>
          <strong>{credentials.length}</strong>
        </article>
        <article>
          <span>Ativas</span>
          <strong>{activeCredentials}</strong>
        </article>
        <article>
          <span>Conta</span>
          <strong>{user.active ? 'Ativa' : 'Inativa'}</strong>
        </article>
      </section>

      {message && <p className="notice wide">{message}</p>}

      <section className="workspace-grid">
        <div className="panel">
          <div className="panel-heading">
            <h2>Nova credencial</h2>
            <span>1 a 1440 min</span>
          </div>

          <form className="inline-form" onSubmit={handleCreateCredential}>
            <label>
              Validade
              <input
                max={1440}
                min={1}
                onChange={(event) => setExpiresInMinutes(Number(event.target.value))}
                required
                type="number"
                value={expiresInMinutes}
              />
            </label>
            <button className="primary-action" disabled={isBusy} type="submit">
              Gerar
            </button>
          </form>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <h2>Validar token</h2>
            <span>Rota publica</span>
          </div>

          <form className="stack-form compact-form" onSubmit={handleValidateCredential}>
            <label>
              Token
              <input
                maxLength={255}
                onChange={(event) => setValidationToken(event.target.value)}
                required
                type="text"
                value={validationToken}
              />
            </label>
            <button className="secondary-action" disabled={isBusy} type="submit">
              Validar
            </button>
          </form>

          {validationResult && (
            <div className={`validation-result ${validationResult.valid ? 'valid' : 'invalid'}`}>
              <strong>{validationResult.status}</strong>
              <span>Expira em {formatDate(validationResult.expires_at)}</span>
            </div>
          )}
        </div>
      </section>

      <section className="credentials-section">
        <div className="section-heading">
          <h2>Credenciais geradas</h2>
          <span>{user.email}</span>
        </div>

        <div className="credentials-list">
          {credentials.length === 0 ? (
            <p className="empty-state">Nenhuma credencial criada ainda.</p>
          ) : (
            credentials.map((credential) => (
              <article className="credential-card" key={credential.id}>
                <div className="credential-main">
                  <span className={credential.revoked ? 'status revoked' : 'status active'}>
                    {credential.revoked ? 'Revogada' : 'Ativa'}
                  </span>
                  <code>{credential.token}</code>
                </div>

                <div className="credential-meta">
                  <span>Criada {formatDate(credential.created_at)}</span>
                  <span>Expira {formatDate(credential.expires_at)}</span>
                </div>

                <div className="credential-actions">
                  <button type="button" onClick={() => handleCopyToken(credential.token)}>
                    Copiar
                  </button>
                  <button
                    disabled={credential.revoked || isBusy}
                    type="button"
                    onClick={() => handleRevokeCredential(credential.id)}
                  >
                    Revogar
                  </button>
                </div>
              </article>
            ))
          )}
        </div>
      </section>
    </main>
  )
}

export default App
