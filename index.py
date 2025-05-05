from app import app, server
import callbacks.callback_report
import callbacks.callback_confronto
import callbacks.callback_crea
import callbacks.callback_impostazioni

if __name__ == "__main__":
    app.run(debug=True)
    
