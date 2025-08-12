router.post("/order", [checkApiPassword, authMiddleware], async (req, res) => {
    try {
        const { packageId, gameId, serverGameId } = req.body;
        const user = req.user;

        if (!packageId || !gameId) {
            return res.status(400).json({ success: false, message: "Missing required parameters" });
        }

        const packageInfo = Packages.find(p => p.id === packageId && p.disabled === false);
        if (!packageInfo) {
            return res.status(400).json({
                success: false,
                message: "Package not found"
            });
        }

        const price = ["reseller", "admin", "superadmin"].includes(user?.role) ? packageInfo.resellerPrice : packageInfo.price;

        if (["reseller", "admin", "superadmin"].includes(user?.role)) {
            const currentUser = await Users.findByPk(user.id);

            if (currentUser.wallet < price) {
                return res.status(401).json({
                    success: false,
                    message: "Insufficient funds"
                });
            }

            await currentUser.decrement('wallet', { by: price });

            const transaction = await createNewTransaction({
                price,
                userId: user.id,
                username: user.username,
                packageInfo: {
                    packageId,
                    ...packageInfo
                },
                gameId,
                serverGameId,
                paymentMethod: "wallet",
                status: "paid",
                clientIP: req.ip
            });

            await sendTransactionNotification(transaction, "Transaction-Pending");

            return res.json(createTransactionResponse(transaction));
        } else {
            const payingTransaction = await Transaction.findAll({
                where: {
                    ip: req.ip,
                    status: "paying",
                    paymentMethod: "qr",
                }
            });

            if (payingTransaction.length >= 5) {
                return res.status(400).json({
                    success: false,
                    message: "You already have 5 or more unpaid orders for this package. Please complete your existing orders first."
                });
            }

            const existingTransaction = await findExistingTransaction({
                price,
                packageId,
                productId: packageInfo.productId,
                gameId,
                serverGameId,
                status: "paying",
                paymentMethod: "qr"
            });

            if (existingTransaction) {
                await handleExistingTransaction(existingTransaction, packageInfo);
                return res.json(createTransactionResponse(existingTransaction));
            }

            const transaction = await createNewTransaction({
                price,
                userId: user?.id,
                username: user?.username,
                packageInfo: {
                    packageId,
                    ...packageInfo
                },
                gameId,
                serverGameId,
                clientIP: req.ip
            });

            await sendTransactionNotification(transaction);

            return res.json(createTransactionResponse(transaction));
        }
    } catch (error) {
         console.log(error);
        return res.status(500).json({
            success: false,
            message: "An error occurred during order processing"
        });
    }
});
