from app import app, server
import callbacks.callback_report
import callbacks.callback_confronto
import callbacks.callback_crea
import callbacks.callback_impostazioni

if __name__ == "__main__":
    app.run(debug=False,
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 8050)))
    
