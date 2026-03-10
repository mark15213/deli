"use client"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [username, setUsername] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { login, register } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isLogin) {
        await login(email, password)
      } else {
        await register(email, password, username || undefined)
      }
      router.push('/feed')
    } catch (err: any) {
      setError(err.message || '操作失败,请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">
            {isLogin ? '登录 Gulp' : '注册 Gulp'}
          </CardTitle>
          <CardDescription className="text-center">
            {isLogin ? '欢迎回来' : '创建你的账号'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="text-sm font-medium text-zinc-700">用户名 (可选)</label>
                <Input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="输入用户名"
                  className="mt-1"
                />
              </div>
            )}

            <div>
              <label className="text-sm font-medium text-zinc-700">邮箱</label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
                className="mt-1"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-zinc-700">密码</label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                minLength={8}
                className="mt-1"
              />
              {!isLogin && (
                <p className="text-xs text-zinc-500 mt-1">至少 8 个字符</p>
              )}
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-zinc-900 hover:bg-zinc-800 text-white"
            >
              {loading ? '处理中...' : isLogin ? '登录' : '注册'}
            </Button>

            <div className="text-center text-sm">
              <button
                type="button"
                onClick={() => {
                  setIsLogin(!isLogin)
                  setError('')
                }}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                {isLogin ? '没有账号? 立即注册' : '已有账号? 立即登录'}
              </button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
