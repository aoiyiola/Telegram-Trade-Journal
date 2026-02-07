export default function ErrorMessage({ message }) {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="card max-w-md w-full text-center border-red-500/50">
        <div className="text-red-500 text-5xl mb-4">⚠️</div>
        <h2 className="text-2xl font-bold text-red-400 mb-2">Oops!</h2>
        <p className="text-gray-300">{message}</p>
        <div className="mt-6">
          <a
            href="https://t.me/YourBotUsername"
            className="btn-primary inline-block"
          >
            Open Telegram Bot
          </a>
        </div>
      </div>
    </div>
  )
}
