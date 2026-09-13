package com.fakenews.server.domain.auth;

import com.fakenews.server.domain.auth.AuthDtos.*;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.Locale;

@Service
@Transactional(readOnly = true)
public class AuthService {
    private final UserRepository users;
    private final PasswordEncoder passwords;
    private final JwtService jwt;

    public AuthService(UserRepository users, PasswordEncoder passwords, JwtService jwt) {
        this.users = users;
        this.passwords = passwords;
        this.jwt = jwt;
    }

    @Transactional
    public UserResponse signUp(SignUpRequest request) {
        String email = normalize(request.email());
        if (users.existsByEmail(email)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "이미 가입된 이메일입니다.");
        }
        return UserResponse.from(users.save(new User(email, passwords.encode(request.password()), request.name().trim())));
    }

    public TokenResponse login(LoginRequest request) {
        User user = users.findByEmail(normalize(request.email())).orElseThrow(this::invalidCredentials);
        if (!passwords.matches(request.password(), user.getPassword())) throw invalidCredentials();
        return new TokenResponse(jwt.createToken(user), "Bearer", jwt.getExpirationSeconds());
    }

    public UserResponse getUser(String email) {
        return users.findByEmail(email).map(UserResponse::from)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "사용자를 찾을 수 없습니다."));
    }

    private String normalize(String email) { return email.trim().toLowerCase(Locale.ROOT); }
    private ResponseStatusException invalidCredentials() {
        return new ResponseStatusException(HttpStatus.UNAUTHORIZED, "이메일 또는 비밀번호가 올바르지 않습니다.");
    }
}
