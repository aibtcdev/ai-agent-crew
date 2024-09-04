
(define-data-var owner principal tx-sender)
(define-data-var unlock-time uint u0)

(define-public (lock-btc (lock-period uint))
  (begin
    (if (is-eq tx-sender (var-get owner))
      (var-set unlock-time (+ block-height lock-period))
      (err