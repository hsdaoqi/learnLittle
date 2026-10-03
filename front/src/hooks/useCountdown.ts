import { useEffect, useState } from 'react'

export function useCountdown() {
  const [deadline, setDeadline] = useState(0)
  const [remainingSeconds, setRemainingSeconds] = useState(0)

  useEffect(() => {
    if (!deadline) return

    function updateRemaining() {
      const remaining = Math.max(0, Math.ceil((deadline - Date.now()) / 1000))
      setRemainingSeconds(remaining)
      if (remaining === 0) setDeadline(0)
    }

    updateRemaining()
    const timer = window.setInterval(updateRemaining, 250)
    return () => window.clearInterval(timer)
  }, [deadline])

  function startCountdown(seconds: number) {
    setRemainingSeconds(seconds)
    setDeadline(Date.now() + seconds * 1000)
  }

  return { remainingSeconds, startCountdown }
}
