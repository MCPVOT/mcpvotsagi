#!/usr/bin/env python3
"""
Wallet Integration for MCPVotsAGI
=================================
Phantom and MetaMask wallet integration for Solana trading
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger("WalletIntegration")

@dataclass
class WalletConnection:
    """Wallet connection information"""
    wallet_type: str  # 'phantom' or 'metamask'
    address: str
    public_key: str
    connected: bool
    network: str  # 'mainnet-beta', 'devnet', 'testnet'

class PhantomWalletAdapter:
    """Phantom wallet adapter for Solana"""
    
    def __init__(self):
        self.connection = None
        
    def get_connection_script(self) -> str:
        """Get JavaScript for Phantom connection"""
        return '''
        async function connectPhantom() {
            if (!window.solana || !window.solana.isPhantom) {
                alert('Phantom wallet not found! Please install Phantom extension.');
                return null;
            }
            
            try {
                const resp = await window.solana.connect();
                const publicKey = resp.publicKey.toString();
                
                // Get network
                const network = await window.solana.request({ method: 'getNetwork' });
                
                return {
                    wallet_type: 'phantom',
                    address: publicKey,
                    public_key: publicKey,
                    connected: true,
                    network: network || 'mainnet-beta'
                };
            } catch (err) {
                console.error('Phantom connection error:', err);
                return null;
            }
        }
        
        async function signPhantomTransaction(transaction) {
            if (!window.solana || !window.solana.isConnected) {
                throw new Error('Phantom not connected');
            }
            
            try {
                const signedTransaction = await window.solana.signTransaction(transaction);
                return signedTransaction;
            } catch (err) {
                console.error('Transaction signing error:', err);
                throw err;
            }
        }
        '''

class MetaMaskAdapter:
    """MetaMask adapter for cross-chain support"""
    
    def __init__(self):
        self.connection = None
        
    def get_connection_script(self) -> str:
        """Get JavaScript for MetaMask connection"""
        return '''
        async function connectMetaMask() {
            if (!window.ethereum || !window.ethereum.isMetaMask) {
                alert('MetaMask not found! Please install MetaMask extension.');
                return null;
            }
            
            try {
                // Request account access
                const accounts = await window.ethereum.request({ 
                    method: 'eth_requestAccounts' 
                });
                
                // Get chain ID
                const chainId = await window.ethereum.request({ 
                    method: 'eth_chainId' 
                });
                
                return {
                    wallet_type: 'metamask',
                    address: accounts[0],
                    public_key: accounts[0],
                    connected: true,
                    network: chainId
                };
            } catch (err) {
                console.error('MetaMask connection error:', err);
                return null;
            }
        }
        
        async function signMetaMaskTransaction(transaction) {
            if (!window.ethereum) {
                throw new Error('MetaMask not connected');
            }
            
            try {
                const signedTransaction = await window.ethereum.request({
                    method: 'eth_signTransaction',
                    params: [transaction]
                });
                return signedTransaction;
            } catch (err) {
                console.error('Transaction signing error:', err);
                throw err;
            }
        }
        '''

def get_wallet_integration_html() -> str:
    """Get HTML/JavaScript for wallet integration"""
    phantom_adapter = PhantomWalletAdapter()
    metamask_adapter = MetaMaskAdapter()
    
    return f'''
    <!-- Wallet Integration Scripts -->
    <script>
        // Phantom Integration
        {phantom_adapter.get_connection_script()}
        
        // MetaMask Integration
        {metamask_adapter.get_connection_script()}
        
        // Universal wallet connection
        let connectedWallet = null;
        
        async function connectWallet(walletType) {{
            let connection = null;
            
            if (walletType === 'phantom') {{
                connection = await connectPhantom();
            }} else if (walletType === 'metamask') {{
                connection = await connectMetaMask();
            }}
            
            if (connection) {{
                connectedWallet = connection;
                updateWalletUI(connection);
                
                // Send to backend
                await fetch('/api/wallet/connect', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(connection)
                }});
                
                return connection;
            }}
            
            return null;
        }}
        
        function updateWalletUI(connection) {{
            const walletDisplay = document.getElementById('walletDisplay');
            if (walletDisplay) {{
                walletDisplay.innerHTML = `
                    <div style="background: #1a1a2e; padding: 10px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
                        <div style="width: 8px; height: 8px; background: #00ff88; border-radius: 50%;"></div>
                        <span style="font-size: 0.9em;">
                            ${{connection.wallet_type === 'phantom' ? '👻' : '🦊'}} 
                            ${{connection.address.substring(0, 6)}}...${{connection.address.substring(connection.address.length - 4)}}
                        </span>
                        <button onclick="disconnectWallet()" style="
                            background: none; 
                            border: 1px solid #ff3838; 
                            color: #ff3838; 
                            padding: 4px 8px; 
                            border-radius: 4px; 
                            cursor: pointer;
                            font-size: 0.8em;
                        ">Disconnect</button>
                    </div>
                `;
            }}
        }}
        
        async function disconnectWallet() {{
            if (connectedWallet) {{
                if (connectedWallet.wallet_type === 'phantom' && window.solana) {{
                    await window.solana.disconnect();
                }}
                
                connectedWallet = null;
                
                // Update UI
                const walletDisplay = document.getElementById('walletDisplay');
                if (walletDisplay) {{
                    walletDisplay.innerHTML = `
                        <button class="btn" onclick="showWalletModal()">Connect Wallet</button>
                    `;
                }}
                
                // Notify backend
                await fetch('/api/wallet/disconnect', {{ method: 'POST' }});
            }}
        }}
        
        function showWalletModal() {{
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
            `;
            
            modal.innerHTML = `
                <div style="background: #1a1a2e; padding: 30px; border-radius: 15px; max-width: 400px; width: 90%;">
                    <h3 style="margin-bottom: 20px;">Connect Wallet</h3>
                    <div style="display: flex; flex-direction: column; gap: 15px;">
                        <button class="btn" onclick="connectWallet('phantom')" style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 10px;">
                            <span style="font-size: 1.5em;">👻</span> Connect Phantom
                        </button>
                        <button class="btn" onclick="connectWallet('metamask')" style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 10px;">
                            <span style="font-size: 1.5em;">🦊</span> Connect MetaMask
                        </button>
                        <button onclick="this.closest('div[style*=\\"position: fixed\\"]').remove()" style="
                            background: none;
                            border: 1px solid #666;
                            color: #888;
                            padding: 10px;
                            border-radius: 8px;
                            cursor: pointer;
                            width: 100%;
                        ">Cancel</button>
                    </div>
                </div>
            `;
            
            modal.onclick = (e) => {{
                if (e.target === modal) {{
                    modal.remove();
                }}
            }};
            
            document.body.appendChild(modal);
        }}
        
        // Check for existing connection on load
        async function checkWalletConnection() {{
            if (window.solana && window.solana.isConnected) {{
                const publicKey = window.solana.publicKey;
                if (publicKey) {{
                    connectedWallet = {{
                        wallet_type: 'phantom',
                        address: publicKey.toString(),
                        public_key: publicKey.toString(),
                        connected: true,
                        network: 'mainnet-beta'
                    }};
                    updateWalletUI(connectedWallet);
                }}
            }}
        }}
        
        // Add to window load
        if (window.addEventListener) {{
            window.addEventListener('load', checkWalletConnection);
        }}
    </script>
    
    <!-- Wallet UI Component -->
    <div id="walletDisplay" style="position: fixed; top: 20px; right: 20px; z-index: 100;">
        <button class="btn" onclick="showWalletModal()">Connect Wallet</button>
    </div>
    '''

class WalletIntegrationAPI:
    """API endpoints for wallet integration"""
    
    def __init__(self):
        self.connected_wallets = {}
        
    async def handle_wallet_connect(self, request):
        """Handle wallet connection"""
        data = await request.json()
        
        wallet_connection = WalletConnection(
            wallet_type=data.get('wallet_type'),
            address=data.get('address'),
            public_key=data.get('public_key'),
            connected=data.get('connected', False),
            network=data.get('network', 'mainnet-beta')
        )
        
        # Store connection
        session_id = request.headers.get('X-Session-Id', 'default')
        self.connected_wallets[session_id] = wallet_connection
        
        logger.info(f"Wallet connected: {wallet_connection.wallet_type} - {wallet_connection.address}")
        
        return {"success": True, "wallet": asdict(wallet_connection)}
    
    async def handle_wallet_disconnect(self, request):
        """Handle wallet disconnection"""
        session_id = request.headers.get('X-Session-Id', 'default')
        
        if session_id in self.connected_wallets:
            wallet = self.connected_wallets[session_id]
            logger.info(f"Wallet disconnected: {wallet.wallet_type} - {wallet.address}")
            del self.connected_wallets[session_id]
        
        return {"success": True}
    
    def get_connected_wallet(self, session_id: str) -> Optional[WalletConnection]:
        """Get connected wallet for session"""
        return self.connected_wallets.get(session_id)