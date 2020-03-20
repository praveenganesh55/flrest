class Edituser(MethodView):
    @token_required
    def get(self, ca, public_id):

        if not ca:
            return jsonify({'message': 'Cannot perform that function!'})

        user = User.query.filter_by(public_id=public_id).first()

        if not user:
            return jsonify({'message': 'No user found!'})

        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin

        return jsonify({'user': user_data})

    @token_required
    def put(self, ca, public_id):
        if not ca:
            return jsonify({'message': 'Cannot perform that function!'})

        user = User.query.filter_by(public_id=public_id).first()

        if not user:
            return jsonify({'message': 'No user found!'})

        user.admin = True
        db.session.commit()

        return jsonify({'message': 'The user has been promoted!'})

    @token_required
    def delete(self, ca, public_id):
        if not ca:
            return jsonify({'message': 'Cannot perform that function!'})

        user = User.query.filter_by(public_id=public_id).first()

        if not user:
            return jsonify({'message': 'No user found!'})

        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': 'The user has been deleted!'})

app.add_url_rule('/user/<public_id>', view_func=Edituser.as_view('Euser'))