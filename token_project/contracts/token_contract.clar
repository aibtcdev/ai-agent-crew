(define-fungible-token my-token
  (uint u1000000))

(define-map balances ((address principal)) ((balance uint)))

(define-public (mint-tokens (recipient principal) (amount uint))
  (begin
    (asserts! (is-eq tx-sender (contract-owner))
      (err u100))
    (let ((current-balance (default-to u0 (get balance (map-get? balances {address: recipient})))))
      (map-set balances {address: recipient} {balance: (+ current-balance amount)}))
    (ft-mint? my-token amount recipient)))

(define-public (transfer-tokens (amount uint) (recipient principal))
  (begin
    (asserts! (>= (default-to u0 (get balance (map-get? balances {address: tx-sender}))) amount)
      (err u101))
    (let ((sender-balance (default-to u0 (get balance (map-get? balances {address: tx-sender}))))
          (recipient-balance (default-to u0 (get balance (map-get? balances {address: recipient}))))
          (new-sender-balance (- sender-balance amount))
          (new-recipient-balance (+ recipient-balance amount)))
      (map-set balances {address: tx-sender} {balance: new-sender-balance})
      (map-set balances {address: recipient} {balance: new-recipient-balance})
      (ft-transfer? my-token amount tx-sender recipient))))

(define-read-only (get-balance (account principal))
  (ok (default-to u0 (get balance (map-get? balances {address: account})))))

(define-public (check-transfer (amount uint) (recipient principal))
  (begin
    (let ((current-balance (default-to u0 (get balance (map-get? balances {address: tx-sender}))))
          (recipient-balance (default-to u0 (get balance (map-get? balances {address: recipient}))))
          (new-sender-balance (- current-balance amount))
          (new-recipient-balance (+ recipient-balance amount)))
      (if (and (>= current-balance amount) (>= new-sender-balance u0))
          (ok true)
          (err u102)))))