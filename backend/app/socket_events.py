import logging
from flask_socketio import emit
from app import socketio
from app.models.scan_model import Scan
from app import db

logger = logging.getLogger(__name__)

@socketio.on('stop_scan')
def handle_stop_scan(data):
    """
    Handle stop scan request from client
    """
    try:
        scan_id = data.get('scan_id')
        if not scan_id:
            emit('scan_stopped', {'success': False, 'message': 'Scan ID required'})
            return
        
        # Find the scan in database
        scan = Scan.query.filter_by(id=scan_id).first()
        if not scan:
            emit('scan_stopped', {'success': False, 'message': 'Scan not found'})
            return
        
        # Update scan status to cancelled/stopped
        scan.status = 'cancelled'
        scan.progress = 0  # Reset progress
        db.session.commit()
        
        # Emit scan stopped event to all clients
        emit('scan_stopped', {
            'success': True,
            'scan_id': scan_id,
            'message': 'Scan stopped successfully'
        })
        
        # Also emit scan progress update to reflect stopped status
        emit('scan_progress', {
            'scan_id': scan_id,
            'progress': 0,
            'status': 'cancelled',
            'stage': 'Scan stopped by user',
            'target': scan.target,
            'scan_type': scan.scan_type
        })
        
        logger.info(f"Scan {scan_id} stopped by user")
        
    except Exception as e:
        logger.error(f"Error stopping scan: {str(e)}")
        emit('scan_stopped', {'success': False, 'message': f'Error stopping scan: {str(e)}'})

@socketio.on('connect')
def handle_connect():
    """
    Handle client connection
    """
    logger.info('Client connected')
    emit('connected', {'message': 'Connected to scanner server'})

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle client disconnection
    """
    logger.info('Client disconnected')
